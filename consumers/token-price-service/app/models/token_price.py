from typing import List
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import Session
from cachetools import TTLCache
import threading

from app.logger.log import get_logger
from app.models.base import Base, get_engine
from app.models.token import Token

# In-memory cache with 60-second TTL — caches all rows per table as a single entry
_price_cache = TTLCache(maxsize=4, ttl=60)
_price_cache_lock = threading.Lock()

logger = get_logger()


class LedgerTokenPrice(Base):
    __tablename__ = "ledger_token_prices"
    id = Column(Integer, primary_key=True)
    resource_address = Column(String)
    usd_price = Column(Float)
    last_updated_at = Column(DateTime)


class LedgerTokenPriceLatest(Base):
    __tablename__ = "ledger_token_prices_latest"
    id = Column(Integer, primary_key=True)
    resource_address = Column(String, unique=True)
    usd_price = Column(Float)
    last_updated_at = Column(DateTime)
    price_source = Column(String, nullable=True)
    fetched_at = Column(DateTime, nullable=True)


def get_ledger_prices_closest_to_timestamp(resource_addresses: list, timestamp: int):
    from datetime import datetime, timedelta

    date = datetime.utcfromtimestamp(timestamp).date()
    start_dt = datetime.combine(date - timedelta(days=1), datetime.min.time())
    end_dt = datetime.combine(date + timedelta(days=1), datetime.max.time())

    with Session(get_engine()) as session:
        result = {}
        for address in resource_addresses:
            closest = (
                session.query(LedgerTokenPrice)
                .filter(LedgerTokenPrice.resource_address == address)
                .filter(LedgerTokenPrice.last_updated_at > start_dt)
                .filter(LedgerTokenPrice.last_updated_at < end_dt)
                .order_by(
                    func.abs(
                        func.extract("epoch", LedgerTokenPrice.last_updated_at)
                        - timestamp
                    )
                )
                .first()
            )
            if closest:
                result[address] = closest
        return result


def _load_all_ledger_prices() -> dict:
    """Fetch all ledger latest prices, return as {resource_address: LedgerTokenPriceLatest}."""
    with _price_cache_lock:
        cached = _price_cache.get("all_ledger")
    if cached is not None:
        return cached

    with Session(get_engine()) as session:
        all_prices = (
            session.query(LedgerTokenPriceLatest)
            .all()
        )
        for price in all_prices:
            price.usd_price = round(price.usd_price, 18)
        session.expunge_all()

    prices_by_address = {p.resource_address: p for p in all_prices}
    with _price_cache_lock:
        _price_cache["all_ledger"] = prices_by_address
    return prices_by_address


def get_ledger_latest_prices(
    resource_addresses: List[str],
) -> List[LedgerTokenPriceLatest]:
    all_prices = _load_all_ledger_prices()
    return [all_prices[addr] for addr in resource_addresses if addr in all_prices]


class LsuPrice:
    resource_address: str
    xrd_redemption_value: float
    usd_price: float

    def __init__(
        self, resource_address: str, xrd_redemption_value: float, xrd_price: float
    ):
        self.resource_address = resource_address
        self.xrd_redemption_value = xrd_redemption_value
        self.usd_price = xrd_price * self.xrd_redemption_value


def get_ledger_latest_price(resource_address: str) -> float:
    all_prices = _load_all_ledger_prices()
    if resource_address in all_prices:
        return all_prices[resource_address].usd_price
    with Session(get_engine()) as session:
        latest_price = (
            session.query(LedgerTokenPriceLatest)
            .filter_by(resource_address=resource_address)
            .first()
        )
        return latest_price.usd_price


def get_whitelisted_tokens():
    with Session(get_engine()) as session:
        latest_prices = {}
        tokens_with_latest_price = (
            session.query(Token, LedgerTokenPriceLatest)
            .filter(Token.allowlist == True)
            .filter(Token.resource_address == LedgerTokenPriceLatest.resource_address)
            .all()
        )

        for token, token_price in tokens_with_latest_price:
            latest_prices[token.id] = {
                "symbol": token.symbol,
                "name": token.name,
                "id": token.id,
                "resource_address": token.resource_address,
                "usd_price": token_price.usd_price,
                "usd_market_cap": "",
                "usd_vol_24h": "",
                "last_updated_at": token_price.last_updated_at,
            }

        return latest_prices



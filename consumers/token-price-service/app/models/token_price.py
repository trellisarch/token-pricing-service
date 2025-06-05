from datetime import datetime, timezone
from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship, Session

from app.logger.log import get_logger
from app.models.base import Base, get_session, get_engine
from app.models.token import Token


logger = get_logger()


def get_prices_closest_to_timestamp(resource_addresses: list, timestamp: int):
    """
    For each resource_address, find the price record from radix_token_prices
    with the closest last_updated_at to the given timestamp.
    Returns a dict: {resource_address: TokenPrice}
    """
    from datetime import datetime, timedelta

    # Convert timestamp to date (YYYY-MM-DD)
    date = datetime.utcfromtimestamp(timestamp).date()
    start_dt = datetime.combine(date - timedelta(days=1), datetime.min.time())
    end_dt = datetime.combine(date + timedelta(days=1), datetime.max.time())

    with Session(get_engine()) as session:
        result = {}
        for address in resource_addresses:
            # Only consider records within +/- 1 day of the date
            closest = (
                session.query(TokenPrice)
                .filter(TokenPrice.resource_address == address)
                .filter(TokenPrice.last_updated_at > start_dt)
                .filter(TokenPrice.last_updated_at < end_dt)
                .order_by(
                    func.abs(
                        func.extract("epoch", TokenPrice.last_updated_at) - timestamp
                    )
                )
                .first()
            )
            if closest:
                result[address] = closest
        return result


class TokenPrice(Base):
    __tablename__ = "radix_token_prices"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, ForeignKey("radix_tokens.resource_address"))
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime)

    token = relationship("Token", back_populates="prices")

    @classmethod
    def insert_new(cls, resource_address: str, usd_price: float):
        session = get_session()
        new_price = cls(
            resource_address=resource_address,
            usd_price=usd_price,
            usd_market_cap=0,
            usd_vol_24h=0,
            last_updated_at=datetime.now(timezone.utc),
        )

        session.add(new_price)
        session.commit()
        return new_price


class LatestTokenPrice(Base):
    __tablename__ = "latest_token_prices"
    id = Column(Integer, primary_key=True)
    resource_address = Column(String)
    usd_price = Column(Float)
    last_updated_at = Column(DateTime)
    allowlist = Column(Boolean)


def get_latest_prices(resource_addresses: List[str]) -> List[LatestTokenPrice]:
    with Session(get_engine()) as session:
        # Query to get the latest prices filtered by resource addresses
        latest_prices = (
            session.query(LatestTokenPrice)
            .filter(LatestTokenPrice.resource_address.in_(resource_addresses))
            .filter(LatestTokenPrice.allowlist == True)
            .all()
        )
        for price in latest_prices:
            price.usd_price = round(price.usd_price, 18)
        return latest_prices


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


def get_latest_price(resource_address: str) -> float:
    with Session(get_engine()) as session:
        latest_price = (
            session.query(TokenPrice)
            .filter_by(resource_address=resource_address)
            .order_by(TokenPrice.last_updated_at.desc())
            .first()
        )
        return latest_price.usd_price


def get_whitelisted_tokens():
    with Session(get_engine()) as session:
        latest_prices = {}
        tokens_with_latest_price = (
            session.query(Token, LatestTokenPrice)
            .filter(Token.allowlist == True)
            .filter(Token.resource_address == LatestTokenPrice.resource_address)
            .all()
        )

        # Populate the dictionary with the results
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

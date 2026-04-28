import logging
from datetime import datetime
from decimal import Decimal

import requests
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, insert

from radixdlt.config.config import Config
from radixdlt.lib.const import COINGECKO_MAPPING
from radixdlt.lib.ledger import get_current_epoch, get_pool_price
from radixdlt.models.base import get_session

Base = declarative_base()


class LedgerTokenPrice(Base):
    __tablename__ = "ledger_token_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String)
    usd_price = Column(DOUBLE_PRECISION)
    last_updated_at = Column(DateTime(timezone=False))


class LedgerTokenPriceLatest(Base):
    __tablename__ = "ledger_token_prices_latest"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String, unique=True)
    usd_price = Column(DOUBLE_PRECISION)
    last_updated_at = Column(DateTime(timezone=False))
    price_source = Column(String, nullable=True)
    fetched_at = Column(DateTime(timezone=False), nullable=True)


class LedgerPriceFetcher:
    @classmethod
    def fetch_and_save_prices(cls, tokens):
        session = get_session()
        now = datetime.utcnow()

        try:
            epoch = get_current_epoch()
            logging.info(f"Current epoch: {epoch}")

            # Fetch CoinGecko USD prices for mapped tokens
            coingecko_prices = cls._fetch_coingecko_prices()

            # Load cached CoinGecko prices from DB for fallback
            cached_cg = cls._load_cached_coingecko_prices(session)

            # Fetch XRD/hUSDC rate from the C9 hUSDC pool in LEDGER_TOKENS
            husdc_config = tokens.get("hUSDC")
            if not husdc_config or not husdc_config["pools"]:
                raise ValueError(
                    "hUSDC must be in LEDGER_TOKENS with at least one pool"
                )
            husdc_pool = next(
                (p for p in husdc_config["pools"] if p["dex"] == "c9"),
                husdc_config["pools"][0],
            )
            xrd_per_husdc = get_pool_price(
                husdc_pool["component"],
                husdc_pool["dex"],
                epoch,
                husdc_pool["base"],
                husdc_pool["quote"],
            )
            husdc_per_xrd = Decimal(1) / xrd_per_husdc
            logging.info(f"hUSDC per XRD: {husdc_per_xrd}")

            for token_name, token_config in tokens.items():
                resource_address = token_config["resource_address"]
                pools = token_config["pools"]
                mapping = COINGECKO_MAPPING.get(token_name)

                # Compute ledger price for all tokens (except XRD which uses baseline)
                ledger_price = None
                if token_name == "XRD":
                    ledger_price = float(husdc_per_xrd)
                elif pools:
                    ledger_price = cls._fetch_ledger_price(
                        token_name, pools, epoch, husdc_per_xrd
                    )

                if mapping:
                    # CoinGecko-weighted token
                    cg_id = mapping["coingecko_id"]
                    weight = mapping.get("weight", Config.COINGECKO_DEFAULT_WEIGHT)
                    cg_price, cg_source = cls._resolve_coingecko_price(
                        token_name,
                        cg_id,
                        coingecko_prices,
                        cached_cg,
                        ledger_price,
                        now,
                    )

                    if cg_price is not None and ledger_price is not None:
                        final_price = (weight * cg_price) + (
                            (1 - weight) * ledger_price
                        )
                        price_source = cg_source
                        fetched_at = (
                            now
                            if cg_source == "coingecko_weighted"
                            else cached_cg.get(cg_id, {}).get("fetched_at")
                        )
                        logging.info(
                            f"{token_name}: cg={cg_price}, ledger={ledger_price}, "
                            f"weight={weight}, final={final_price}, source={price_source}"
                        )
                    elif cg_price is not None:
                        final_price = cg_price
                        price_source = cg_source
                        fetched_at = (
                            now
                            if cg_source == "coingecko_weighted"
                            else cached_cg.get(cg_id, {}).get("fetched_at")
                        )
                        logging.warning(
                            f"{token_name}: no ledger price, using CoinGecko only: {final_price}"
                        )
                    elif ledger_price is not None:
                        final_price = ledger_price
                        price_source = "ledger_only"
                        fetched_at = None
                        logging.warning(
                            f"{token_name}: no CoinGecko price, using ledger only: {final_price}"
                        )
                    else:
                        logging.error(f"{token_name}: no price available, skipping")
                        continue

                    cls._save_price(
                        session,
                        resource_address,
                        final_price,
                        now,
                        price_source,
                        fetched_at,
                    )
                else:
                    # Ledger-only token
                    if ledger_price is None:
                        logging.error(f"{token_name}: all pools failed, skipping")
                        continue

                    logging.info(f"{token_name}: ledger_only usd_price={ledger_price}")
                    cls._save_price(
                        session,
                        resource_address,
                        ledger_price,
                        now,
                        "ledger_only",
                        None,
                    )

            session.commit()
            logging.info("All ledger prices saved successfully")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def _fetch_coingecko_prices(cls):
        """Fetch USD prices from CoinGecko for all mapped coin IDs."""
        coin_ids = list({m["coingecko_id"] for m in COINGECKO_MAPPING.values()})
        headers = {
            "accept": "application/json",
        }
        try:
            response = requests.get(
                url=f"{Config.COIN_GECKO_API}/simple/price",
                params={"ids": ",".join(coin_ids), "vs_currencies": "USD"},
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                prices = {
                    coin_id: data[coin_id]["usd"]
                    for coin_id in coin_ids
                    if coin_id in data and "usd" in data[coin_id]
                }
                logging.info(f"CoinGecko prices fetched: {prices}")
                return prices
            else:
                logging.error(
                    f"CoinGecko API error: {response.status_code} {response.text}"
                )
                return {}
        except Exception as e:
            logging.error(f"CoinGecko API request failed: {e}")
            return {}

    @classmethod
    def _load_cached_coingecko_prices(cls, session):
        """Load the last known CoinGecko prices from ledger_token_prices_latest."""
        cached = {}
        rows = (
            session.query(LedgerTokenPriceLatest)
            .filter(LedgerTokenPriceLatest.fetched_at.isnot(None))
            .all()
        )
        # Build a reverse lookup: resource_address -> coingecko_id
        addr_to_cg_id = {}
        for token_name, mapping in COINGECKO_MAPPING.items():
            from radixdlt.lib.const import LEDGER_TOKENS

            if token_name in LEDGER_TOKENS:
                addr = LEDGER_TOKENS[token_name]["resource_address"]
                addr_to_cg_id[addr] = mapping["coingecko_id"]

        for row in rows:
            cg_id = addr_to_cg_id.get(row.resource_address)
            if cg_id and cg_id not in cached:
                cached[cg_id] = {
                    "usd_price": row.usd_price,
                    "fetched_at": row.fetched_at,
                }
        return cached

    @classmethod
    def _resolve_coingecko_price(
        cls,
        token_name,
        cg_id,
        coingecko_prices,
        cached_cg,
        ledger_price,
        now,
    ):
        """Resolve the CoinGecko price to use: fresh, cached, or None."""
        threshold = Config.COINGECKO_DIVERGENCE_THRESHOLD
        staleness = Config.COINGECKO_STALENESS_THRESHOLD_SECS

        # Try fresh CoinGecko price
        if cg_id in coingecko_prices:
            cg_price = coingecko_prices[cg_id]

            # Divergence check against ledger
            if ledger_price and ledger_price > 0:
                divergence = abs(cg_price - ledger_price) / ledger_price
                if divergence > threshold:
                    logging.warning(
                        f"{token_name}: CoinGecko price {cg_price} diverges "
                        f"{divergence:.1%} from ledger {ledger_price} "
                        f"(threshold {threshold:.0%}), rejecting fresh price"
                    )
                    # Fall through to cached price
                else:
                    return cg_price, "coingecko_weighted"
            else:
                return cg_price, "coingecko_weighted"

        # Try cached CoinGecko price
        if cg_id in cached_cg:
            cached = cached_cg[cg_id]
            age = (now - cached["fetched_at"]).total_seconds()
            if age <= staleness:
                logging.info(
                    f"{token_name}: using cached CoinGecko price "
                    f"(age={age:.0f}s, limit={staleness}s)"
                )
                return cached["usd_price"], "coingecko_cached"
            else:
                logging.warning(
                    f"{token_name}: cached CoinGecko price too stale "
                    f"(age={age:.0f}s > {staleness}s)"
                )

        return None, None

    @classmethod
    def _fetch_ledger_price(cls, token_name, pools, epoch, husdc_per_xrd):
        """Fetch and average ledger DEX price across pools."""
        pool_usd_prices = []
        for pool in pools:
            component = pool["component"]
            dex = pool["dex"]
            base = pool["base"]
            quote = pool["quote"]
            logging.info(
                f"Fetching {token_name} from {dex} pool {component} ({base}/{quote})"
            )
            try:
                xrd_per_token = get_pool_price(component, dex, epoch, base, quote)
                usd_price = xrd_per_token * husdc_per_xrd
                logging.info(
                    f"{token_name} [{dex}]: xrd_per_token={xrd_per_token}, "
                    f"usd_price={usd_price}"
                )
                pool_usd_prices.append(usd_price)
            except Exception as e:
                logging.error(
                    f"Failed to fetch {token_name} from {dex} pool {component}: {e}"
                )

        if not pool_usd_prices:
            return None

        avg = float(sum(pool_usd_prices) / len(pool_usd_prices))
        logging.info(
            f"{token_name}: avg_ledger_usd_price={avg} "
            f"(from {len(pool_usd_prices)} pools)"
        )
        return avg

    @classmethod
    def _save_price(
        cls,
        session,
        resource_address,
        usd_price,
        last_updated_at,
        price_source=None,
        fetched_at=None,
    ):
        # Append to historical table
        session.add(
            LedgerTokenPrice(
                resource_address=resource_address,
                usd_price=usd_price,
                last_updated_at=last_updated_at,
            )
        )

        # Upsert into latest table
        values = {
            "resource_address": resource_address,
            "usd_price": usd_price,
            "last_updated_at": last_updated_at,
            "price_source": price_source,
            "fetched_at": fetched_at,
        }
        update_set = {
            "usd_price": usd_price,
            "last_updated_at": last_updated_at,
            "price_source": price_source,
        }
        # Only update fetched_at when we have a fresh CoinGecko price
        if fetched_at is not None:
            update_set["fetched_at"] = fetched_at

        stmt = (
            insert(LedgerTokenPriceLatest)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["resource_address"],
                set_=update_set,
            )
        )
        session.execute(stmt)

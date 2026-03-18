import logging
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, insert

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


class LedgerPriceFetcher:
    @classmethod
    def fetch_and_save_prices(cls, tokens):
        session = get_session()
        now = datetime.utcnow()

        try:
            epoch = get_current_epoch()
            logging.info(f"Current epoch: {epoch}")

            # Fetch XRD/hUSDC rate from the C9 hUSDC pool in LEDGER_TOKENS
            husdc_config = tokens.get("hUSDC")
            if not husdc_config or not husdc_config["pools"]:
                raise ValueError("hUSDC must be in LEDGER_TOKENS with at least one pool")
            husdc_pool = next(
                (p for p in husdc_config["pools"] if p["dex"] == "c9"),
                husdc_config["pools"][0],
            )
            husdc_per_xrd = get_pool_price(
                husdc_pool["component"], husdc_pool["dex"], epoch,
                husdc_pool["base"], husdc_pool["quote"],
            )
            logging.info(f"hUSDC per XRD: {husdc_per_xrd}")

            for token_name, token_config in tokens.items():
                resource_address = token_config["resource_address"]
                pools = token_config["pools"]

                if token_name == "XRD":
                    usd_price = float(husdc_per_xrd)
                    logging.info(f"XRD: usd_price={usd_price}")
                    cls._save_price(session, resource_address, usd_price, now)
                    continue

                if token_name == "hUSDC":
                    logging.info("hUSDC: usd_price=1.0")
                    cls._save_price(session, resource_address, 1.0, now)
                    continue

                # Fetch price from each pool, log individually, then average
                # get_pool_price returns XRD per token (normalized)
                # USD price = xrd_per_token * husdc_per_xrd
                pool_usd_prices = []
                for pool in pools:
                    component = pool["component"]
                    dex = pool["dex"]
                    base = pool["base"]
                    quote = pool["quote"]
                    logging.info(f"Fetching {token_name} from {dex} pool {component} ({base}/{quote})")
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
                    logging.error(f"{token_name}: all pools failed, skipping")
                    continue

                avg_usd_price = float(
                    sum(pool_usd_prices) / len(pool_usd_prices)
                )
                logging.info(
                    f"{token_name}: avg_usd_price={avg_usd_price} "
                    f"(from {len(pool_usd_prices)} pools)"
                )
                cls._save_price(session, resource_address, avg_usd_price, now)

            session.commit()
            logging.info("All ledger prices saved successfully")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def _save_price(cls, session, resource_address, usd_price, last_updated_at):
        # Append to historical table
        session.add(
            LedgerTokenPrice(
                resource_address=resource_address,
                usd_price=usd_price,
                last_updated_at=last_updated_at,
            )
        )

        # Upsert into latest table
        stmt = (
            insert(LedgerTokenPriceLatest)
            .values(
                resource_address=resource_address,
                usd_price=usd_price,
                last_updated_at=last_updated_at,
            )
            .on_conflict_do_update(
                index_elements=["resource_address"],
                set_={
                    "usd_price": usd_price,
                    "last_updated_at": last_updated_at,
                },
            )
        )
        session.execute(stmt)

import logging
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert

from radixdlt.lib.const import LEDGER_USD_POOL
from radixdlt.lib.ledger import get_current_epoch, get_pool_price
from radixdlt.models.base import get_session

Base = declarative_base()


class LedgerTokenPrice(Base):
    __tablename__ = "ledger_token_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String)
    usd_price = Column(Float)
    last_updated_at = Column(DateTime(timezone=False))


class LedgerTokenPriceLatest(Base):
    __tablename__ = "ledger_token_prices_latest"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String, unique=True)
    usd_price = Column(Float)
    last_updated_at = Column(DateTime(timezone=False))


class LedgerPriceFetcher:
    @classmethod
    def fetch_and_save_prices(cls, tokens):
        session = get_session()
        now = datetime.utcnow()

        try:
            epoch = get_current_epoch()
            logging.info(f"Current epoch: {epoch}")

            # Fetch XRD/hUSDC price first — this is our USD conversion rate
            xrd_usd_price = get_pool_price(
                LEDGER_USD_POOL["component"], LEDGER_USD_POOL["dex"], epoch,
            )
            logging.info(f"XRD/hUSDC price (USD proxy): {xrd_usd_price}")

            for token_name, token_config in tokens.items():
                resource_address = token_config["resource_address"]
                pools = token_config["pools"]

                if token_name == "XRD":
                    usd_price = float(xrd_usd_price)
                    logging.info(f"XRD: usd_price={usd_price}")
                    cls._save_price(session, resource_address, usd_price, now)
                    continue

                if token_name == "hUSDC":
                    logging.info("hUSDC: usd_price=1.0")
                    cls._save_price(session, resource_address, 1.0, now)
                    continue

                # Fetch price from each pool, log individually, then average
                pool_usd_prices = []
                for pool in pools:
                    component = pool["component"]
                    dex = pool["dex"]
                    logging.info(f"Fetching {token_name} from {dex} pool {component}")
                    pool_price = get_pool_price(component, dex, epoch)
                    usd_price = xrd_usd_price / pool_price
                    logging.info(
                        f"{token_name} [{dex}]: pool_price={pool_price}, "
                        f"usd_price={usd_price}"
                    )
                    pool_usd_prices.append(usd_price)

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

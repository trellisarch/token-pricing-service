import logging
import requests
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from radixdlt.config.config import Config
from radixdlt.lib.http import get_radix_charts_headers
from radixdlt.models.base import get_session

Base = declarative_base()


class RadixTokenPrice(Base):
    __tablename__ = "radix_token_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String)
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime(timezone=False))
    token_id = Column(Integer)


class RadixTokenPriceLatest(Base):
    __tablename__ = "radix_token_prices_latest"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String)
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime(timezone=False))
    token_id = Column(Integer, unique=True)


class PriceFetcher:
    @classmethod
    def fetch_and_save_prices(cls, tokens):
        session = get_session()
        current_price_endpoint = Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT
        chunked_tokens = [tokens[i : i + 30] for i in range(0, len(tokens), 30)]

        for chunk in chunked_tokens:
            addresses = ",".join(token[0] for token in chunk)
            logging.info(f"Getting prices for {len(chunk)} addresses")
            params = {"resource_addresses": addresses}
            response = requests.get(
                url=current_price_endpoint,
                params=params,
                headers=get_radix_charts_headers(),
            )
            price_data = response.json().get("data", {})
            logging.info(price_data)

            for resource_address, data in price_data.items():
                dt = datetime.fromtimestamp(data["last_updated_at"])

                new_price = RadixTokenPrice(
                    resource_address=resource_address,
                    token_id=None,
                    usd_price=data["usd_price"],
                    usd_market_cap=data["usd_market_cap"],
                    usd_vol_24h=data["usd_vol_24h"],
                    last_updated_at=dt,
                )
                session.add(new_price)

                stmt = (
                    insert(RadixTokenPriceLatest)
                    .values(
                        resource_address=resource_address,
                        token_id=None,
                        usd_price=data["usd_price"],
                        usd_market_cap=data["usd_market_cap"],
                        usd_vol_24h=data["usd_vol_24h"],
                        last_updated_at=dt,
                    )
                    .on_conflict_do_update(
                        index_elements=["resource_address"],
                        set_={
                            "resource_address": resource_address,
                            "usd_price": data["usd_price"],
                            "usd_market_cap": data["usd_market_cap"],
                            "usd_vol_24h": data["usd_vol_24h"],
                            "last_updated_at": dt,
                        },
                    )
                )
                session.execute(stmt)
        session.commit()

        try:
            logging.info("Refreshing materialized view")
            session.execute(
                "REFRESH MATERIALIZED VIEW CONCURRENTLY latest_token_prices"
            )
            session.commit()
        except Exception as e:
            logging.error(f"Failed to refresh materialized view: {e}")
            session.rollback()
        finally:
            session.close()

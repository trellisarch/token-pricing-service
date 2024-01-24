import logging

import requests
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from radixdlt.config.config import Config
from radixdlt.lib.http import get_radix_charts_headers
from radixdlt.models.base import get_session

Base = declarative_base()


class RadixTokenPrice(Base):
    __tablename__ = 'radix_token_prices'
    resource_address = Column(String, primary_key=True)
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime)

    @classmethod
    def fetch_and_save_prices(cls, tokens):
        session = get_session()
        current_price_endpoint = Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT
        chunked_tokens = [tokens[i: i + 30] for i in range(0, len(tokens), 30)]

        for chunk in chunked_tokens:
            addresses = ",".join(token[0] for token in chunk)

            logging.info(addresses)
            params = {"resource_addresses": addresses}
            response = requests.get(url=current_price_endpoint,
                                    params=params,
                                    headers=get_radix_charts_headers())
            logging.info(response.text)
            logging.info(get_radix_charts_headers())
            price_data = response.json()["data"]
            logging.info(price_data)

            for resource_address in price_data.keys():
                existing_price = session.query(cls).filter_by(resource_address=resource_address).first()
                if not existing_price:
                    new_price = cls(
                        resource_address=resource_address,
                        usd_price=price_data[resource_address]["usd_price"],
                        usd_market_cap=price_data[resource_address]["usd_market_cap"],
                        usd_vol_24h=price_data[resource_address]["usd_vol_24h"],
                        last_updated_at=datetime.fromtimestamp(
                            price_data[resource_address]["last_updated_at"]
                        ),
                    )
                    session.add(new_price)

        session.commit()
        session.close()

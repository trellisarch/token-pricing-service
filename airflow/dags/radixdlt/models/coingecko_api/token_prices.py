from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from typing import List, Tuple
import time


import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from sqlalchemy import Column, Integer, DateTime, String, Float, BigInteger, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from radixdlt.config.config import Config
from radixdlt.models.base import get_session

Base = declarative_base()


class CoinGeckoTokenData(Base):
    __tablename__ = "coingecko_token_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    price = Column(Float)
    volume = Column(BigInteger)
    marketcap = Column(BigInteger)
    weeklyMovingAvgPrice = Column(Float)
    weeklyMovingAvgVolume = Column(Float)
    weeklyMovingAvgMarketCap = Column(Float)
    last_updated_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"({self.id} {self.symbol} {self.price} {self.volume}, {self.marketcap}, {self.weeklyMovingAvgPrice} {self.weeklyMovingAvgVolume} {self.weeklyMovingAvgMarketCap} {self.last_updated_at})"

    @classmethod
    def fetch_and_save_data(cls, token):
        # for each token fetch the coinggecko output and then fetch last records for last seven days and calculate average along with new value
        currency = "usd"
        time.sleep(10)  # Sleep 10 second so not to hit rate limit
        start_time = datetime.today() - timedelta(days=7)
        price_data = CoinGeckoTokenData.get_token_prices(token, currency)
        logging.info(price_data)
        if price_data is None:
            raise Exception("Failed to retrieve data from Coingecko API")

        new_price = price_data["prices"][0][1]
        new_volume = price_data["total_volumes"][0][1]
        new_marketcap = price_data["market_caps"][0][1]
        try:
            with get_session() as session:
                dt_object = datetime.fromtimestamp(
                    int(price_data["prices"][0][0]) / 1000
                )
                existingtokenData = (
                    session.query(CoinGeckoTokenData)
                    .filter(CoinGeckoTokenData.symbol == token)
                    .filter(CoinGeckoTokenData.last_updated_at >= start_time)
                )
                weeklyAvgs = CoinGeckoTokenData.get_weekly_average(
                    existingtokenData, new_price, new_volume, new_marketcap
                )
                new_metric = cls(
                    symbol=token,
                    price=new_price,
                    volume=new_volume,
                    marketcap=new_marketcap,
                    weeklyMovingAvgPrice=weeklyAvgs["weeklyMovingAvgPrice"],
                    weeklyMovingAvgVolume=weeklyAvgs["weeklyMovingAvgVolume"],
                    weeklyMovingAvgMarketCap=weeklyAvgs["weeklyMovingAvgMarketCap"],
                    last_updated_at=dt_object,
                )
                session.add(new_metric)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

    @staticmethod
    def get_token_prices(token: String, currency: String):
        logging.info(f"Getting metrics for package: {token}")

        api_base_url = Config.COIN_GECKO_API
        url = f"{api_base_url}/coins/{token}/market_chart?vs_currency={currency}&days=1&interval=daily"
        print(url)
        headers = {
            "x-cg-pro-api-key": Config.COIN_GECKO_API_KEY,
            "accept": "application/json",
        }
        try:
            retry = Retry(
                total=5,
                backoff_factor=3,
                status_forcelist=[429],
            )
            adapter = HTTPAdapter(max_retries=retry)
            rq_session = requests.Session()
            rq_session.mount("https://", adapter)

            response = rq_session.get(url, headers=headers, timeout=300)
            print(response.status_code)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_weekly_average(existingTokenData, price, volume, marketcap):
        items = 1
        prices_sum = price
        volume_sum = volume
        market_cap_sum = marketcap
        for data in existingTokenData:
            prices_sum = data.price + prices_sum
            volume_sum = data.volume + volume_sum
            market_cap_sum = data.marketcap + market_cap_sum
            items = items + 1
        return {
            "weeklyMovingAvgPrice": prices_sum / items,
            "weeklyMovingAvgVolume": volume_sum / items,
            "weeklyMovingAvgMarketCap": market_cap_sum / items,
        }

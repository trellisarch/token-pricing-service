import logging

from sqlalchemy import Column, String, Float, DateTime, Integer, desc
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from radixdlt.models.base import get_session

Base = declarative_base()


class C9Price(Base):
    __tablename__ = "c9_lsu_price"
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    source_address = Column(String)
    timestamp = Column(DateTime)

    @classmethod
    def insert_c9_price(cls, price, source_address):
        session = get_session()
        new_price = cls(
            price=price,
            timestamp=datetime.utcnow(),
            source_address=source_address,
        )
        session.add(new_price)
        session.commit()

    @staticmethod
    def get_average_price() -> float:
        session = get_session()
        now = datetime.utcnow()
        six_minutes_ago = now - timedelta(minutes=6)

        prices_query = (
            session.query(C9Price.price)
            .filter(C9Price.timestamp >= six_minutes_ago)
            .order_by(desc(C9Price.timestamp))
            .limit(5)
        )

        prices = [price for price, in prices_query]
        logging.info(f"Latest LSULP prices: {prices}")
        if prices:
            return sum(prices) / len(prices)
        else:
            return 0.0

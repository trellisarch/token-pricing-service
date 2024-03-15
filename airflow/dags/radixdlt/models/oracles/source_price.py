import logging

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from radixdlt.models.base import get_session

Base = declarative_base()


class OracleSourcePrice(Base):
    __tablename__ = "oracle_source_prices"
    id = Column(Integer, primary_key=True)
    pair = Column(String)
    quote = Column(Float)
    quote_source = Column(String)
    timestamp = Column(DateTime)
    last_updated = Column(Integer)

    @classmethod
    def insert_source_price(cls, pair, quote, quote_source, last_updated):
        session = get_session()
        new_price = cls(
            pair=pair,
            quote=quote,
            quote_source=quote_source,
            timestamp=datetime.utcnow(),
            last_updated=last_updated,
        )
        session.add(new_price)
        session.commit()

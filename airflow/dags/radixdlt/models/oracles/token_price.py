from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from radixdlt.models.base import get_session

Base = declarative_base()


class OracleTokenPrice(Base):
    __tablename__ = 'oracle_token_prices'
    id = Column(Integer, primary_key=True)
    pair = Column(String)
    quote = Column(Float)
    quote_source = Column(String)
    timestamp = Column(DateTime)

    @classmethod
    def insert_price(cls, pair, quote, quote_source):
        session = get_session()
        new_price = cls(pair=pair,
                        quote=quote,
                        quote_source=quote_source,
                        timestamp=datetime.utcnow())
        session.add(new_price)
        session.commit()

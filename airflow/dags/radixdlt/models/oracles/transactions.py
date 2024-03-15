import logging

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from radixdlt.models.base import get_session

Base = declarative_base()


class OracleTransaction(Base):
    __tablename__ = "oracle_transactions"
    id = Column(Integer, primary_key=True)
    pair = Column(String)
    quote = Column(Float)
    quote_source = Column(String)
    timestamp = Column(DateTime)
    transaction_id = Column(String)

    @classmethod
    def insert_transaction(cls, pair, quote, quote_source, transaction):
        session = get_session()
        new_transaction = cls(
            pair=pair,
            quote=quote,
            quote_source=quote_source,
            transaction=transaction,
            timestamp=datetime.utcnow(),
        )
        session.add(new_transaction)
        session.commit()

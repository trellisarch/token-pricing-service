from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.exc import IntegrityError
from app.logger.log import get_logger
from app.models.base import Base, get_session

logger = get_logger()


class Token(Base):
    __tablename__ = "radix_tokens"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, unique=True)
    symbol = Column(String)
    name = Column(String)
    allowlist = Column(Boolean)

    @classmethod
    def insert_new(cls, resource_address: str, symbol: str, name: str):
        session = get_session()
        new_token = cls(name=name, symbol=symbol, resource_address=resource_address)
        try:
            session.add(new_token)
            session.commit()
            return new_token
        except IntegrityError:
            session.rollback()
            existing_token = (
                session.query(cls).filter_by(resource_address=resource_address).first()
            )
            return existing_token

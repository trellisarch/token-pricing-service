from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, Session
from app.logger.log import get_logger
from app.models.base import Base, get_session, get_engine
from app.models.token_price import TokenPrice

logger = get_logger()


class Token(Base):
    __tablename__ = "radix_tokens"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, unique=True)
    symbol = Column(String)
    name = Column(String)

    prices = relationship("TokenPrice", back_populates="token")

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

    @classmethod
    def get_latest_prices(cls):
        with Session(get_engine()) as session:
            latest_prices = {}

            # Query to fetch the latest price for each token using a correlated subquery
            tokens_with_latest_price = (
                session.query(cls, TokenPrice)
                .filter(cls.resource_address == TokenPrice.resource_address)
                .order_by(cls.id, TokenPrice.last_updated_at.desc())
                .distinct(cls.id)
                .all()
            )

            # Populate the dictionary with the results
            for token, token_price in tokens_with_latest_price:
                latest_prices[token.id] = {
                    "symbol": token.symbol,
                    "name": token.name,
                    "id": token.id,
                    "resource_address": token.resource_address,
                    "usd_price": token_price.usd_price,
                    "usd_market_cap": token_price.usd_market_cap,
                    "usd_vol_24h": token_price.usd_vol_24h,
                    "last_updated_at": token_price.last_updated_at,
                }

            return latest_prices

from time import sleep

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
            tokens = session.query(cls).all()
            for token in tokens:
                latest_price = (
                    session.query(TokenPrice)
                    .filter_by(resource_address=token.resource_address)
                    .order_by(TokenPrice.last_updated_at.desc())
                    .first()
                )
                if latest_price:
                    latest_prices[token.symbol] = {
                        "id": latest_price.id,
                        "resource_address": latest_price.resource_address,
                        "name": token.name,
                        "symbol": token.symbol,
                        "usd_price": latest_price.usd_price,
                        "usd_market_cap": latest_price.usd_market_cap,
                        "usd_vol_24h": latest_price.usd_vol_24h,
                        "last_updated_at": latest_price.last_updated_at,
                    }
            return latest_prices


def get_price_for_resource_address(resource_address) -> TokenPrice:
    with Session(get_engine()) as session:
        token = (
            session.query(Token).filter_by(resource_address=resource_address).first()
        )
        if token:
            prices = token.prices
            if prices:
                return prices[0].usd_price
            else:
                return None
        else:
            return None

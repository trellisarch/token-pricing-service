import datetime
from typing import List

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session

from app.models.base import Base, get_session, get_engine


class TokenPrice(Base):
    __tablename__ = "radix_token_prices"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, ForeignKey("radix_tokens.resource_address"))
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime)

    token = relationship("Token", back_populates="prices")

    @classmethod
    def insert_new(cls, resource_address: str, usd_price: float):
        session = get_session()
        new_price = cls(
            resource_address=resource_address,
            usd_price=usd_price,
            usd_market_cap=0,
            usd_vol_24h=0,
            last_updated_at=datetime.datetime.now(),
        )

        session.add(new_price)
        session.commit()
        return new_price


class LsuPrice:
    resource_address: str
    xrd_redemption_value: float
    usd_price: float

    def __init__(
        self, resource_address: str, xrd_redemption_value: float, xrd_price: float
    ):
        self.resource_address = resource_address
        self.xrd_redemption_value = xrd_redemption_value
        self.usd_price = xrd_price * self.xrd_redemption_value


def get_latest_prices(resource_addresses: List[str]) -> List[TokenPrice]:
    with Session(get_engine()) as session:
        latest_prices = (
            session.query(TokenPrice)
            .filter(TokenPrice.resource_address.in_(resource_addresses))
            .order_by(TokenPrice.resource_address, TokenPrice.last_updated_at.desc())
            .distinct(TokenPrice.resource_address)
            .all()
        )
        return latest_prices


def get_latest_price(resource_address: str) -> float:
    with Session(get_engine()) as session:
        latest_price = (
            session.query(TokenPrice)
            .filter_by(resource_address=resource_address)
            .order_by(TokenPrice.last_updated_at.desc())
            .first()
        )
        return latest_price.usd_price

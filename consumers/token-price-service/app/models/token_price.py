from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base, get_session


class TokenPrice(Base):
    __tablename__ = "token_prices"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, ForeignKey("tokens.resource_address"))
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime)

    token = relationship("Token", back_populates="prices")


class LsuPrice:
    resource_address: str
    xrd_redemption_value: float

    def __init__(self, resource_address: str, xrd_redemption_value: float):
        self.resource_address = resource_address
        self.xrd_redemption_value = xrd_redemption_value


def get_latest_price(resource_address: str) -> TokenPrice:
    latest_price = (
        get_session()
        .query(TokenPrice)
        .filter(TokenPrice.resource_address == resource_address)
        .order_by(TokenPrice.last_updated_at.desc())
        .first()
    )
    return latest_price

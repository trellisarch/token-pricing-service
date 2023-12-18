from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, unique=True)
    symbol = Column(String)
    name = Column(String)


class TokenPrice(Base):
    __tablename__ = 'token_prices'

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, ForeignKey('tokens.resource_address'))
    usd_price = Column(Float)
    usd_market_cap = Column(Float)
    usd_vol_24h = Column(Float)
    last_updated_at = Column(DateTime)

    token = relationship("Token", backref="prices")

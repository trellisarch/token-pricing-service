from sqlalchemy import Column, Integer, String, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from app.models.base import Base, get_session
from app.models.token_price import TokenPrice


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


def get_price_for_resource_address(resource_address) -> TokenPrice:
    session = get_session()
    token = session.query(Token).filter_by(resource_address=resource_address).first()
    if token:
        prices = token.prices
        if prices:
            return prices[0].usd_price
        else:
            return None
    else:
        return None


def fetch_tokens_with_latest_price():
    session = get_session()
    subq = (
        session.query(
            TokenPrice.resource_address,
            func.max(TokenPrice.last_updated_at).label("max_date"),
        )
        .group_by(TokenPrice.resource_address)
        .subquery()
    )

    query = (
        session.query(Token, TokenPrice)
        .join(TokenPrice, TokenPrice.resource_address == Token.resource_address)
        .join(
            subq,
            and_(
                TokenPrice.resource_address == subq.c.resource_address,
                TokenPrice.last_updated_at == subq.c.max_date,
            ),
        )
        .filter(TokenPrice.last_updated_at == subq.c.max_date)
    )

    tokens_with_latest_price = query.all()
    return tokens_with_latest_price

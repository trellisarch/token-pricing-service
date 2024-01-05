from time import sleep

from sqlalchemy import Column, Integer, String, func, and_
from sqlalchemy.orm import relationship

from app.logger.log import get_logger
from app.models.base import Base, get_session
from app.models.token_price import TokenPrice


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    resource_address = Column(String, unique=True)
    symbol = Column(String)
    name = Column(String)

    prices = relationship("TokenPrice", back_populates="token")


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

import logging

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from radixdlt.models.base import get_session

Base = declarative_base()


class RadixToken(Base):
    __tablename__ = "radix_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String, unique=True, nullable=False)
    symbol = Column(String)
    name = Column(String)
    allowlist = Column(Boolean)

    @classmethod
    def insert_tokens(cls, tokens):
        session = get_session()
        existing_tokens = session.query(cls).all()

        # Update existing tokens and mark those not present in `tokens` as not whitelisted
        for existing_token in existing_tokens:
            logging.info(f"Checking existing token: {existing_token.resource_address}")
            if existing_token.resource_address in tokens.keys():
                logging.info(
                    f"Token: {existing_token.resource_address} returned by radix charts"
                )
                token_data = tokens[existing_token.resource_address]
                existing_token.symbol = token_data["symbol"]
                existing_token.name = token_data["name"]
                existing_token.allowlist = True
            else:
                logging.info(
                    f"Token: {existing_token.resource_address} not returned by radix charts. Removing from whitelist"
                )
                existing_token.allowlist = False

        # Add new tokens
        for resource_address, token_data in tokens.items():
            if resource_address not in [
                token.resource_address for token in existing_tokens
            ]:
                logging.info(f"Resource {resource_address} is new. Adding it")
                new_token = cls(
                    resource_address=resource_address,
                    symbol=token_data["symbol"],
                    name=token_data["name"],
                    allowlist=True,  # By default, newly added tokens are whitelisted
                )
                session.add(new_token)

        session.commit()
        session.close()

    @classmethod
    def list_tokens(cls):
        session = get_session()
        return (
            session.query(cls.resource_address)
            .filter_by(allowlist=True)
            .distinct()
            .all()
        )

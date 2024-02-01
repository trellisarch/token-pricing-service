from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from radixdlt.models.base import get_session

Base = declarative_base()


class RadixToken(Base):
    __tablename__ = "radix_tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_address = Column(String, unique=True, nullable=False)
    symbol = Column(String)
    name = Column(String)

    @classmethod
    def insert_tokens(cls, tokens):
        session = get_session()
        for resource_address, token_data in tokens.items():
            existing_token = (
                session.query(cls).filter_by(resource_address=resource_address).first()
            )
            if not existing_token:
                new_token = cls(
                    resource_address=resource_address,
                    symbol=token_data["symbol"],
                    name=token_data["name"],
                )
                session.add(new_token)

        session.commit()
        session.close()

    @classmethod
    def list_tokens(cls):
        session = get_session()
        return session.query(cls.resource_address).distinct().all()

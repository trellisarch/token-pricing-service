from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from radixdlt.lib.psql import get_postgres_connection

Base = declarative_base()


class Token(Base):
    __tablename__ = 'tokens'
    resource_address = Column(String, primary_key=True)
    symbol = Column(String)
    name = Column(String)

    @classmethod
    def insert_tokens(cls, tokens):
        engine = get_postgres_connection()
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for resource_address, token_data in tokens.items():
            existing_token = session.query(cls).filter_by(resource_address=resource_address).first()
            if not existing_token:
                new_token = cls(
                    resource_address=resource_address,
                    symbol=token_data["symbol"],
                    name=token_data["name"],
                )
                session.add(new_token)

        session.commit()
        session.close()

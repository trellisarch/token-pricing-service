from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from radixdlt.config.config import Config

engine = create_engine(Config.DB_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def get_session() -> Session:
    return Session()

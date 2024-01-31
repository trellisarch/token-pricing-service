from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.config import Config


engine = create_engine(Config.DB_URI, pool_size=0)
Session = sessionmaker(bind=engine)
Base = declarative_base()


def get_session() -> Session:
    return Session()

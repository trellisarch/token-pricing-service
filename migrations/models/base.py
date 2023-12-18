import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://radix:radix@postgres_radix:5432/radix_data"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SQLAlchemy()

# Create all tables
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)


def init_db(app):
    logger.debug("Initializing DB")
    db.init_app(app)
    db.create_all()

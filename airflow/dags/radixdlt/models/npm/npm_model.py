import logging
from datetime import datetime

import requests
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from radixdlt.config.config import Config
from radixdlt.models.base import get_session

Base = declarative_base()


class NpmMetricsModel(Base):
    __tablename__ = "npm_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    package_name = Column(String)
    downloads = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, package):
        period = "last-day"
        logging.info(f"Getting metrics for package: {package}")
        url = f"https://api.npmjs.org/downloads/point/{period}/{package}"
        response = requests.get(url)

        if response.status_code == 200:
            downloads = response.json()["downloads"]
        else:
            raise
        try:
            with get_session() as session:
                new_metric = cls(
                    downloads=downloads,
                    package_name=package,
                )
                session.add(new_metric)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            session.close()
            logging.error(f"Error occurred: {e}")
            raise SQLAlchemyError

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session
import requests

Base = declarative_base()


class CratesData(Base):
    __tablename__ = "crates_io_downloads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    package = Column(String, nullable=False)
    downloads = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, package):
        # Extract relevant user information

        downloads = get_crate_downloads(package)
        try:
            with get_session() as session:
                new_info = cls(
                    downloads=downloads,
                    package=package,
                )
                logging.info(f"""downloads: {new_info.downloads}, 
                        package: {new_info.package},""")
                session.add(new_info)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")


def get_crate_downloads(crate_name):
    url = f"https://crates.io/api/v1/crates/{crate_name}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        downloads = data["crate"]["downloads"]
        logging.info(f"""downloads: {downloads}, 
                crate_name: {crate_name}""")
        return downloads
    else:
        print(
            f"Failed to fetch data for crate '{crate_name}'. HTTP Status Code: {response.status_code}"
        )
        return None

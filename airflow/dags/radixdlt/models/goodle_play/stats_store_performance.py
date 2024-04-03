import logging
import sqlalchemy
from pandas import DataFrame
from sqlalchemy.orm import declarative_base
from radixdlt.models.base import get_session

Base = declarative_base()


class GooglePlayStorePerformance(Base):
    __tablename__ = "google_play_store_performance"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    package_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    country = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    store_listing_acquisitions = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    store_listing_visitors = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    store_listing_conversion_rate = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    @classmethod
    def insert_csv_data(cls, stats_data_frame: DataFrame):
        session = get_session()
        stats_data_frame.columns = [
            col.lower().replace(" ", "_") for col in stats_data_frame.columns
        ]
        for index, row in stats_data_frame.iterrows():
            # Check if the combination of date, package name, and version exists in the database
            existing_row = (
                session.query(cls)
                .filter(
                    cls.date == row["date"],
                    cls.package_name == row["package_name"],
                    cls.country == str(row["country_/_region"]),
                )
                .first()
            )

            # If the row doesn't exist, insert it
            if not existing_row:
                session.add(
                    cls(
                        date=row["date"],
                        package_name=row["package_name"],
                        country=row["country_/_region"],
                        store_listing_acquisitions=row["store_listing_acquisitions"],
                        store_listing_visitors=row["store_listing_visitors"],
                        store_listing_conversion_rate=row[
                            "store_listing_conversion_rate"
                        ],
                    )
                )

        session.commit()
        logging.info("Data inserted successfully!")

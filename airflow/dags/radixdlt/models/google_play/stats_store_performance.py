import logging
import sqlalchemy
from pandas import DataFrame
from sqlalchemy.orm import declarative_base
from radixdlt.models.base import get_session
from radixdlt.config.config import Config

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

        # Initialize the boolean to False (no condition is violated)
        missing_data = False

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

            # List of column names and their log message formats
            columns = [
                (
                    "total_store_acquisitions",
                    f"Row{index} : total_store_acquisitions: {{}}",
                ),
                ("store_listing_visitors", f"Row{index}: store_listing_visitors: {{}}"),
                (
                    "store_listing_conversion_rate",
                    f"Row{index}: store_listing_conversion_rate: {{}}",
                ),
            ]

            # Iterate over the column names
            for column, log_msg in columns:
                if column in row:
                    logging.info(log_msg.format(row[column]))
                else:
                    missing_data = True  # Set to True if any column is missing

            # If the row doesn't exist, insert it
            if not existing_row:
                session.add(
                    cls(
                        date=row["date"],
                        package_name=row["package_name"],
                        country=row["country_/_region"],
                        store_listing_acquisitions=row.get(
                            "total_store_acquisitions", None
                        ),
                        store_listing_visitors=row.get("store_listing_visitors", None),
                        store_listing_conversion_rate=row.get(
                            "store_listing_conversion_rate", None
                        ),
                    )
                )

        # Log stats if any data is missing
        if missing_data:
            Config.statsDClient.incr(
                f"dag_google_play.missing_data_stats_store_performance.missed"
            )
        else:
            Config.statsDClient.incr(
                f"dag_google_play.missing_data_stats_store_performance.passed"
            )
        session.commit()
        logging.info("Data inserted successfully!")

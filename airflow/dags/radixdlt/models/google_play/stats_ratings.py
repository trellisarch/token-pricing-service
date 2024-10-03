import logging
import sqlalchemy
from pandas import DataFrame
from sqlalchemy.orm import declarative_base
from radixdlt.models.base import get_session

Base = declarative_base()


class GooglePlayRatings(Base):
    __tablename__ = "google_play_ratings"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    package_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    app_version_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    daily_avg_rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    total_avg_rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

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
                    cls.app_version_code == str(row["app_version_code"]),
                )
                .first()
            )

            # If the row doesn't exist, insert it
            if not existing_row:
                session.add(
                    cls(
                        date=row["date"],
                        package_name=row["package_name"],
                        app_version_code=row["app_version_code"],
                        daily_avg_rating=row["daily_average_rating"],
                        total_avg_rating=row["total_average_rating"],
                    )
                )

        session.commit()
        logging.info("Data inserted successfully!")

import logging
import sqlalchemy
from pandas import DataFrame
from sqlalchemy.orm import declarative_base
from radixdlt.models.base import get_session

Base = declarative_base()


class GooglePlayInstalls(Base):
    __tablename__ = "google_play_installs"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    package_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    app_version_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    daily_device_installs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    daily_device_uninstalls = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    daily_device_upgrades = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    total_user_installs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    daily_user_installs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    daily_user_uninstalls = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    active_device_installs = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    install_events = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    update_events = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    uninstall_events = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    @classmethod
    def insert_csv_data(cls, stats_data_frame: DataFrame):
        session = get_session()
        stats_data_frame.columns = [
            col.lower().replace(" ", "_") for col in stats_data_frame.columns
        ]
        for index, row in stats_data_frame.iterrows():
            # Check if the combination of date, package name, and version exists in the database
            existing_row = (
                session.query(GooglePlayInstalls)
                .filter(
                    GooglePlayInstalls.date == row["date"],
                    GooglePlayInstalls.package_name == row["package_name"],
                    GooglePlayInstalls.app_version_code == str(row["app_version_code"]),
                )
                .first()
            )

            # If the row doesn't exist, insert it
            if not existing_row:
                session.add(
                    GooglePlayInstalls(
                        date=row["date"],
                        package_name=row["package_name"],
                        app_version_code=row["app_version_code"],
                        daily_device_installs=row["daily_device_installs"],
                        daily_device_uninstalls=row["daily_device_uninstalls"],
                        daily_device_upgrades=row["daily_device_upgrades"],
                        total_user_installs=row["total_user_installs"],
                        daily_user_installs=row["daily_user_installs"],
                        daily_user_uninstalls=row["daily_user_uninstalls"],
                        active_device_installs=row["active_device_installs"],
                        install_events=row["install_events"],
                        update_events=row["update_events"],
                        uninstall_events=row["uninstall_events"],
                    )
                )

        session.commit()
        logging.info("Data inserted successfully!")

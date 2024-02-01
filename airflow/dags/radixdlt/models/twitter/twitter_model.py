import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class TwitterData(Base):
    __tablename__ = "twitter"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    followers_count = Column(Integer)
    friends_count = Column(Integer)
    statuses_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, api_response):
        # Extract relevant user information
        followers_count = api_response.followers_count
        friends_count = api_response.friends_count
        statuses_count = api_response.statuses_count

        logging.info(
            f"""Followers Count: {followers_count}, 
                     Friends Count: {friends_count}, 
                     Statuses Count: {statuses_count}"""
        )

        try:
            session = get_session()

            new_info = cls(
                account=account,
                followers_count=followers_count,
                friends_count=friends_count,
                statuses_count=statuses_count,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

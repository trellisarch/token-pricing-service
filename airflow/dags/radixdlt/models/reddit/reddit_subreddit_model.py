import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class RedditSubredditData(Base):
    __tablename__ = "reddit_subreddit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    subscribers_count = Column(Integer)
    active_user_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, api_response):

        # Extract relevant user information
        subscribers_count = api_response.subscribers
        active_user_count = api_response.active_user_count

        # To get traffic, PRAW should authenticate with username and password
        # https://praw.readthedocs.io/en/stable/getting_started/faq.html
        # traffic = api_response.traffic

        logging.info(
            f"""user: {account},
                     subscribers_count: {subscribers_count}, 
                     active_user_count: {active_user_count}"""
        )

        try:
            session = get_session()

            new_info = cls(
                account=account,
                subscribers_count=subscribers_count,
                active_user_count=active_user_count,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

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
    unique_pageviews = Column(Integer)
    total_pageviews = Column(Integer)
    subscribers = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, api_response):
        # Extract relevant user information
        subscribers_count = api_response.subscribers
        active_user_count = getattr(api_response, "accounts_active", 0)

        try:
            traffic = api_response.traffic()

            data_day = traffic["day"][1]

            unique_pageviews = total_pageviews = subscribers = 0

            unique_pageviews = data_day[1]
            total_pageviews = data_day[2]
            subscribers = data_day[3]

        except Exception as traffic_error:
            logging.error(f"Could not retrieve traffic information: {traffic_error}")
            unique_pageviews = 0
            total_pageviews = 0
            subscribers = 0

        logging.info(f"""user: {account},
                subscribers_count: {subscribers_count}, 
                active_user_count: {active_user_count},
                unique_pageviews: {unique_pageviews},
                total_pageviews: {total_pageviews},
                subscribers: {subscribers}
            """)

        try:
            session = get_session()

            new_info = cls(
                account=account,
                subscribers_count=subscribers_count,
                active_user_count=active_user_count,
                unique_pageviews=unique_pageviews,
                total_pageviews=total_pageviews,
                subscribers=subscribers,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

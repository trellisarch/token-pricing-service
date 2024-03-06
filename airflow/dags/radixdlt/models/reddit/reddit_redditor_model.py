import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class RedditRedditorData(Base):
    __tablename__ = "reddit_redditor"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    comment_karma = Column(Integer)
    link_karma = Column(Integer)
    total_karma = Column(Integer)
    trophy_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, api_response):
        # Extract relevant user information
        comment_karma = api_response.comment_karma
        link_karma = api_response.link_karma
        total_karma = comment_karma + link_karma
        trophy_count = len([trophy.name for trophy in api_response.trophies()])

        logging.info(
            f"""user: {account},
                     comment_karma: {comment_karma}, 
                     link_karma: {link_karma}, 
                     total_karma: {total_karma},
                     trophy_count: {trophy_count}"""
        )

        try:
            session = get_session()

            new_info = cls(
                account=account,
                comment_karma=comment_karma,
                link_karma=link_karma,
                total_karma=total_karma,
                trophy_count=trophy_count,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

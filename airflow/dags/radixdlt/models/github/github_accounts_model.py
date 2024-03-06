import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class GithubAccountsData(Base):
    __tablename__ = "github_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    public_repos_total = Column(Integer)
    followers_total = Column(Integer)
    gists_total = Column(Integer)
    following_total = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, api_response):
        # Extract relevant user information
        public_repos_total = api_response.get_repos().totalCount
        followers_total = api_response.get_followers().totalCount
        gists_total = api_response.get_gists().totalCount
        following_total = api_response.get_following().totalCount

        logging.info(
            f"""public_repos_total: {public_repos_total}, 
                followers_total: {followers_total}, 
                gists_total: {gists_total}, 
                following_total: {following_total}"""
        )

        try:
            session = get_session()

            new_info = cls(
                account=account,
                public_repos_total=public_repos_total,
                followers_total=followers_total,
                gists_total=gists_total,
                following_total=following_total,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

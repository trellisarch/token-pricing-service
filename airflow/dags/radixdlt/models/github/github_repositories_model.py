import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class GithubRepositoriesData(Base):
    __tablename__ = "github_repositories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    repository = Column(String, nullable=False)
    commits = Column(Integer)
    branches = Column(Integer)
    pr_all = Column(Integer)
    pr_open = Column(Integer)
    pr_closed = Column(Integer)
    issues_all = Column(Integer)
    issues_open = Column(Integer)
    issues_closed = Column(Integer)
    contributors = Column(Integer)
    releases = Column(Integer)
    subscribers = Column(Integer)
    tags = Column(Integer)
    watchers = Column(Integer)
    clones_traffic = Column(Integer)
    clones_traffic_unique = Column(Integer)
    views_traffic = Column(Integer)
    views_traffic_unique = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, repository, api_response):
        logging.info(f"api_response: {api_response}")

        # Extract relevant repository information
        commits = api_response.get_commits().totalCount
        branches = api_response.get_branches().totalCount
        pr_all = api_response.get_pulls(state="all").totalCount
        pr_open = api_response.get_pulls(state="open").totalCount
        pr_closed = api_response.get_pulls(state="closed").totalCount
        issues_all = api_response.get_issues(state="all").totalCount - pr_all
        issues_open = api_response.get_issues(state="open").totalCount - pr_open
        issues_closed = api_response.get_issues(state="closed").totalCount - pr_closed
        contributors = api_response.get_contributors().totalCount
        releases = api_response.get_releases().totalCount
        subscribers = api_response.get_subscribers().totalCount
        tags = api_response.get_tags().totalCount
        watchers = api_response.get_watchers().totalCount

        try:
            # Resource not accessible by personal access token
            clones_traffic = api_response.get_clones_traffic()["count"]
            clones_traffic_unique = api_response.get_clones_traffic()["uniques"]
            views_traffic = api_response.get_views_traffic()["count"]
            views_traffic_unique = api_response.get_views_traffic()["uniques"]

        except Exception as traffic_error:
            logging.warning(f"Could not retrieve traffic information: {traffic_error}")
            clones_traffic = 0
            clones_traffic_unique = 0
            views_traffic = 0
            views_traffic_unique = 0

        logging.info(
            f"""commits:{commits},
                branches:{branches},
                pr_all:{pr_all},
                pr_open:{pr_open},
                pr_closed:{pr_closed},
                issues_all:{issues_all},
                issues_open:{issues_open},
                issues_closed:{issues_closed},
                contributors:{contributors},
                releases:{releases},
                subscribers:{subscribers},
                tags:{tags},
                watchers:{watchers},
                clones_traffic:{clones_traffic},
                clones_traffic_unique:{clones_traffic_unique},
                views_traffic:{views_traffic},
                views_traffic_unique:{views_traffic_unique},
                """
        )

        try:
            session = get_session()

            new_info = cls(
                account=account,
                repository=repository,
                commits=commits,
                branches=branches,
                pr_all=pr_all,
                pr_open=pr_open,
                pr_closed=pr_closed,
                issues_all=issues_all,
                issues_open=issues_open,
                issues_closed=issues_closed,
                contributors=contributors,
                releases=releases,
                subscribers=subscribers,
                tags=tags,
                watchers=watchers,
                clones_traffic=clones_traffic,
                clones_traffic_unique=clones_traffic_unique,
                views_traffic=views_traffic,
                views_traffic_unique=views_traffic_unique,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

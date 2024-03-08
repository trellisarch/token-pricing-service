import logging
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session
import googleapiclient.discovery

Base = declarative_base()


class YoutubeData(Base):
    __tablename__ = "youtube"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    total_views = Column(Integer)
    average_watchtime = Column(Integer)
    new_subs = Column(Integer)
    lost_subs = Column(Integer)
    estimated_minutes_watched = Column(Integer)
    annotation_impressions = Column(Integer)
    average_view_percentage = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, channel, credentials):
        youtubeAnalytics = googleapiclient.discovery.build(
            "youtubeAnalytics", "v2", credentials=credentials
        )

        start_date = datetime.now() - timedelta(days=3)
        end_date = datetime.now() - timedelta(days=2)

        request = youtubeAnalytics.reports().query(
            ids=f"channel=={channel}",
            startDate=start_date.strftime("%Y-%m-%d"),
            endDate=end_date.strftime("%Y-%m-%d"),
            metrics="views,averageViewDuration,subscribersGained,subscribersLost,estimatedMinutesWatched,annotationImpressions,averageViewPercentage",
        )
        response = request.execute()

        headers = [
            "views",
            "averageViewDuration",
            "subscribersGained",
            "subscribersLost",
            "estimatedMinutesWatched",
            "annotationImpressions",
            "averageViewPercentage",
        ]

        data_dict = {
            header: value for header, value in zip(headers, response["rows"][0])
        }

        logging.info(
            f"""views: {data_dict['views']}, 
                averageViewDuration: {data_dict['averageViewDuration']}, 
                subscribersGained: {data_dict['subscribersGained']}, 
                subscribersLost: {data_dict['subscribersLost']}, 
                estimatedMinutesWatched: {data_dict['estimatedMinutesWatched']},
                annotationImpressions: {data_dict['annotationImpressions']},
                averageViewPercentage: {data_dict['averageViewPercentage']}"""
        )

        try:
            with get_session() as session:
                new_info = cls(
                    account=account,
                    total_views=data_dict["views"],
                    average_watchtime=data_dict["averageViewDuration"],
                    new_subs=data_dict["subscribersGained"],
                    lost_subs=data_dict["subscribersLost"],
                    estimated_minutes_watched=data_dict["estimatedMinutesWatched"],
                    annotation_impressions=data_dict["annotationImpressions"],
                    average_view_percentage=data_dict["averageViewPercentage"],
                )
                session.add(new_info)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

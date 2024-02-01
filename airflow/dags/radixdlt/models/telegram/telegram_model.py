import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class TelegramData(Base):
    __tablename__ = "telegram"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account = Column(String, nullable=False)
    members_total = Column(Integer)
    week_messages_total = Column(Integer)
    week_new_users_total = Column(Integer)
    week_left_users_total = Column(Integer)
    week_active_users_total = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, bot_response, combot_response):

        # Extract relevant user information
        members_total = bot_response
        combot_data = combot_response

        week_messages_total = sum([msg[1] for msg in combot_data["messages"]])
        week_new_users_total = combot_data["new_users_total"]
        week_left_users_total = combot_data["left_users_total"]
        week_active_users_total = combot_data["active_users_total"]

        logging.info(f"AAAA {members_total}, type: {type(members_total)}")

        logging.info(
            f"""Member Count: {members_total}, 
                     Messages Total: {week_messages_total}, 
                     New Users Total: {week_new_users_total}, 
                     Left Users Total: {week_left_users_total}, 
                     Active Users Total: {week_active_users_total}"""
        )

        try:
            with get_session() as session:

                new_info = cls(
                    account=account,
                    members_total=members_total,
                    week_messages_total=week_messages_total,
                    week_new_users_total=week_new_users_total,
                    week_left_users_total=week_left_users_total,
                    week_active_users_total=week_active_users_total,
                )
                session.add(new_info)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

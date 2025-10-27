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
    messages_total = Column(Integer)
    new_users_total = Column(Integer)
    left_users_total = Column(Integer)
    active_users_total = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(cls, account, bot_response, combot_response):
        # Extract relevant user information
        members_total = bot_response
        combot_data = combot_response if combot_response else {}

        # Handle combot data with defaults for missing fields
        messages = combot_data.get("messages", [])
        messages_total = (
            messages[0][1]
            if messages and len(messages) > 0 and len(messages[0]) > 1
            else None
        )
        new_users_total = combot_data.get("new_users_total")
        left_users_total = combot_data.get("left_users_total")
        active_users_total = combot_data.get("active_users_total")

        logging.info(
            f"""Member Count: {members_total}, 
                Messages Total: {messages_total}, 
                New Users Total: {new_users_total}, 
                Left Users Total: {left_users_total}, 
                Active Users Total: {active_users_total}"""
        )

        try:
            with get_session() as session:
                new_info = cls(
                    account=account,
                    members_total=members_total,
                    messages_total=messages_total,
                    new_users_total=new_users_total,
                    left_users_total=left_users_total,
                    active_users_total=active_users_total,
                )
                session.add(new_info)
                logging.info("Data inserted successfully.")
                session.commit()
                session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Float, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class BalanceHistory(Base):
    __tablename__ = "acc_comp_monitoring_balance_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_address = Column(String, nullable=False)
    resource_address = Column(String, nullable=False)
    resource_name = Column(String)
    balance = Column(Float, nullable=False)
    previous_balance = Column(Float)
    balance_change = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def get_previous_balance(cls, account_address: str, resource_address: str) -> float:
        """Get the most recent balance for an account/resource pair."""
        session = get_session()
        try:
            result = (
                session.query(cls)
                .filter(
                    cls.account_address == account_address,
                    cls.resource_address == resource_address,
                )
                .order_by(desc(cls.timestamp))
                .first()
            )
            return result.balance if result else None
        except SQLAlchemyError as e:
            logging.error(f"Database error getting previous balance: {e}")
            raise
        finally:
            session.close()

    @classmethod
    def save_balance(
        cls,
        account_address: str,
        resource_address: str,
        resource_name: str,
        balance: float,
        previous_balance: float,
    ):
        """Save a new balance record."""
        balance_change = None
        if previous_balance is not None:
            balance_change = balance - previous_balance

        session = get_session()
        try:
            new_record = cls(
                account_address=account_address,
                resource_address=resource_address,
                resource_name=resource_name,
                balance=balance,
                previous_balance=previous_balance,
                balance_change=balance_change,
            )
            session.add(new_record)
            session.commit()
            logging.info(
                f"Balance saved: {account_address[:20]}... {resource_name} = {balance} (change: {balance_change})"
            )
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Database error saving balance: {e}")
            raise
        finally:
            session.close()

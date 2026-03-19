import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session

Base = declarative_base()


class NetworkData(Base):
    __tablename__ = "network"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tx_count_24h = Column(Float)
    created_accounts_24h = Column(Float)
    tx_count_7d = Column(Float)
    created_accounts_7d = Column(Float)
    tx_count_30d = Column(Float)
    created_accounts_30d = Column(Float)
    tx_count_total = Column(Float)
    created_accounts_total = Column(Float)
    tvl = Column(Float)
    staked_xrd = Column(Float)
    hourly_burnt_amount = Column(Float)
    daily_burnt_amount = Column(Float)
    weekly_burnt_amount = Column(Float)
    monthly_burnt_amount = Column(Float)
    annually_burnt_amount = Column(Float)
    remaining_supply = Column(Float)
    burnt_amount = Column(Float)
    max_supply = Column(Float)
    current_block = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(
        cls,
        ##response_five,
        ##response_burn,
        response_defillama,
        response_radixapi,
    ):
        # Extract relevant user information
        # Parse the JSON response
        # if response_five.status_code == 200:
        #     data_five = response_five.json()
        #     price = data_five["data"]["price"]
        #     hourly_burnt_amount = data_five["data"]["hourlyBurntAmount"]
        #     daily_burnt_amount = data_five["data"]["dailyBurntAmount"]
        #     weekly_burnt_amount = data_five["data"]["weeklyBurntAmount"]
        #     monthly_burnt_amount = data_five["data"]["monthlyBurntAmount"]
        #     annually_burnt_amount = data_five["data"]["annuallyBurntAmount"]
        # else:
        #     logging.info(
        #         f"Did not get a successful response from burn trucker: {response_five.status_code}"
        #     )
        #     price = 0
        #     hourly_burnt_amount = 0
        #     daily_burnt_amount = 0
        #     weekly_burnt_amount = 0
        #     monthly_burnt_amount = 0
        #     annually_burnt_amount = 0

        # if response_burn.status_code == 200:
        #     data_burn = response_burn.json()
        #     remaining_supply = data_burn["tokenDetail"][
        #         "totalSupply"
        #     ]  # For some reason the webpage uses totalSupply instead of remainingSupply
        #     burnt_amount = data_burn["tokenDetail"]["burntAmount"]
        #     max_supply = data_burn["tokenDetail"]["maxSupply"]
        #     current_block = data_burn["tokenDetail"]["currentBlock"]
        # else:
        #     logging.info(
        #         f"Did not get a successful response from burn trucker: {response_five.status_code}"
        #     )
        #     remaining_supply = 0
        #     burnt_amount = 0
        #     max_supply = 0
        #     current_block = 0

        tvl = response_defillama.json()[-1]["tvl"]
        radixapi_stats = response_radixapi.json()

        tx_count_24h = radixapi_stats["data"]["24h"]["transaction_count"]
        created_accounts_24h = radixapi_stats["data"]["24h"]["created_accounts"]
        tx_count_7d = radixapi_stats["data"]["7d"]["transaction_count"]
        created_accounts_7d = radixapi_stats["data"]["7d"]["created_accounts"]
        tx_count_30d = radixapi_stats["data"]["30d"]["transaction_count"]
        created_accounts_30d = radixapi_stats["data"]["30d"]["created_accounts"]
        tx_count_total = radixapi_stats["data"]["total"]["transaction_count"]
        created_accounts_total = radixapi_stats["data"]["total"]["created_accounts"]
        staked_xrd = radixapi_stats["data"]["total"]["staked_xrd"]

        logging.info(f"""tx_count_24h: {tx_count_24h},
                created_accounts_24h: {created_accounts_24h},
                tx_count_7d: {tx_count_7d},
                created_accounts_7d: {created_accounts_7d},
                tx_count_30d: {tx_count_30d},
                created_accounts_30d: {created_accounts_30d},
                tx_count_total: {tx_count_total},
                created_accounts_total: {created_accounts_total},
                tvl: {tvl},
                staked_xrd: {staked_xrd}
            """)

        ##Deleted logging
        # hourly_burnt_amount: {hourly_burnt_amount},
        # daily_burnt_amount: {daily_burnt_amount},
        # weekly_burnt_amount: {weekly_burnt_amount},
        # monthly_burnt_amount: {monthly_burnt_amount},
        # annually_burnt_amount: {annually_burnt_amount},
        # remaining_supply: {remaining_supply},
        # burnt_amount: {burnt_amount},
        # max_supply: {max_supply},
        # current_block: {current_block},
        # price: {price},
        try:
            session = get_session()

            new_info = cls(
                tx_count_24h=tx_count_24h,
                created_accounts_24h=created_accounts_24h,
                tx_count_7d=tx_count_7d,
                created_accounts_7d=created_accounts_7d,
                tx_count_30d=tx_count_30d,
                created_accounts_30d=created_accounts_30d,
                tx_count_total=tx_count_total,
                created_accounts_total=created_accounts_total,
                tvl=tvl,
                staked_xrd=staked_xrd,
            )

            ### Deleted burn:
            # hourly_burnt_amount=hourly_burnt_amount,
            # daily_burnt_amount=daily_burnt_amount,
            # weekly_burnt_amount=weekly_burnt_amount,
            # monthly_burnt_amount=monthly_burnt_amount,
            # annually_burnt_amount=annually_burnt_amount,
            # remaining_supply=remaining_supply,
            # burnt_amount=burnt_amount,
            # max_supply=max_supply,
            # current_block=current_block,
            # price=price,

            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")
            raise
        finally:
            session.close()

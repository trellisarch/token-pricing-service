import logging
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from radixdlt.models.base import get_session


Base = declarative_base()


class TokensData(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(String, nullable=False)
    symbol = Column(String)
    market_cap_usd = Column(Float)
    total_volume_usd = Column(Float)
    sentiment_votes_up_percentage = Column(Float)
    sentiment_votes_down_percentage = Column(Float)
    watchlist_portfolio_users = Column(Float)
    market_cap_rank = Column(Float)
    current_price = Column(Float)
    total_value_locked_usd = Column(Float)
    total_value_locked_btc = Column(Float)
    mcap_to_tvl_ratio = Column(Float)
    fdv_to_tvl_ratio = Column(Float)
    ath = Column(Float)
    ath_change_percentage = Column(Float)
    ath_date = Column(DateTime)
    atl = Column(Float)
    atl_change_percentage = Column(Float)
    atl_date = Column(DateTime)
    fully_diluted_valuation = Column(Float)
    market_cap_fdv_ratio = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    circulating_supply = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

    @classmethod
    def fetch_and_save_data(
        cls,
        token_id,
        response_api,
    ):
        token_response = response_api.json()

        symbol = token_response["symbol"]
        market_cap_usd = token_response["market_data"]["market_cap"]["usd"]
        total_volume_usd = token_response["market_data"]["total_volume"]["usd"]

        try:
            sentiment_votes_up_percentage = (
                token_response.get("sentiment_votes_up_percentage", 0) or 0
            )
            sentiment_votes_down_percentage = (
                token_response.get("sentiment_votes_down_percentage", 0) or 0
            )
            watchlist_portfolio_users = (
                token_response.get("watchlist_portfolio_users", 0) or 0
            )
            market_cap_rank = token_response.get("market_cap_rank", 0) or 0

            market_data = token_response.get("market_data", {})
            current_price = market_data.get("current_price", {}).get("usd", 0) or 0

            total_value_locked = market_data.get("total_value_locked", {}) or {}
            total_value_locked_usd = total_value_locked.get("usd", 0) or 0
            total_value_locked_btc = total_value_locked.get("btc", 0) or 0

            mcap_to_tvl_ratio = market_data.get("mcap_to_tvl_ratio", 0) or 0
            fdv_to_tvl_ratio = market_data.get("fdv_to_tvl_ratio", 0) or 0
            ath = market_data.get("ath", {}).get("usd", 0) or 0
            ath_change_percentage = (
                market_data.get("ath_change_percentage", {}).get("usd", 0) or 0
            )
            ath_date = (
                market_data.get("ath_date", {}).get("usd", "Unknown Date")
                or "Unknown Date"
            )
            atl = market_data.get("atl", {}).get("usd", 0) or 0
            atl_change_percentage = (
                market_data.get("atl_change_percentage", {}).get("usd", 0) or 0
            )
            atl_date = (
                market_data.get("atl_date", {}).get("usd", "Unknown Date")
                or "Unknown Date"
            )
            fully_diluted_valuation = (
                market_data.get("fully_diluted_valuation", {}).get("usd", 0) or 0
            )
            market_cap_fdv_ratio = market_data.get("market_cap_fdv_ratio", 0) or 0
            high_24h = market_data.get("high_24h", {}).get("usd", 0) or 0
            low_24h = market_data.get("low_24h", {}).get("usd", 0) or 0
            circulating_supply = market_data.get("circulating_supply", 0) or 0

        except Exception as traffic_error:
            logging.error(f"Could not retrieve traffic information: {traffic_error}")

        logging.info(
            f"""
                token_id: {token_id},
                symbol: {symbol},
                token_market_cap_usd: {market_cap_usd},
                token_total_volume_usd: {total_volume_usd},
                sentiment_votes_up_percentage: {sentiment_votes_up_percentage}, 
                sentiment_votes_down_percentage: {sentiment_votes_down_percentage}, 
                watchlist_portfolio_users: {watchlist_portfolio_users},
                market_cap_rank: {market_cap_rank},
                current_price: {current_price}, 
                total_value_locked_usd: {total_value_locked_usd},
                total_value_locked_btc: {total_value_locked_btc}, 
                mcap_to_tvl_ratio: {mcap_to_tvl_ratio}, 
                fdv_to_tvl_ratio: {fdv_to_tvl_ratio}, 
                ath: {ath},
                ath_change_percentage: {ath_change_percentage}, 
                ath_date: {ath_date}, 
                atl: {atl}, 
                atl_change_percentage: {atl_change_percentage}, 
                atl_date: {atl_date},
                fully_diluted_valuation: {fully_diluted_valuation}, 
                market_cap_fdv_ratio: {market_cap_fdv_ratio}, 
                high_24h: {high_24h}, 
                low_24h: {low_24h}, 
                circulating_supply: {circulating_supply},
            """
        )

        try:
            session = get_session()

            new_info = cls(
                token_id=token_id,
                symbol=symbol,
                market_cap_usd=market_cap_usd,
                total_volume_usd=total_volume_usd,
                sentiment_votes_up_percentage=sentiment_votes_up_percentage,
                sentiment_votes_down_percentage=sentiment_votes_down_percentage,
                watchlist_portfolio_users=watchlist_portfolio_users,
                market_cap_rank=market_cap_rank,
                current_price=current_price,
                total_value_locked_usd=total_value_locked_usd,
                total_value_locked_btc=total_value_locked_btc,
                mcap_to_tvl_ratio=mcap_to_tvl_ratio,
                fdv_to_tvl_ratio=fdv_to_tvl_ratio,
                ath=ath,
                ath_change_percentage=ath_change_percentage,
                ath_date=ath_date,
                atl=atl,
                atl_change_percentage=atl_change_percentage,
                atl_date=atl_date,
                fully_diluted_valuation=fully_diluted_valuation,
                market_cap_fdv_ratio=market_cap_fdv_ratio,
                high_24h=high_24h,
                low_24h=low_24h,
                circulating_supply=circulating_supply,
            )
            session.add(new_info)
            logging.info("Data inserted successfully.")
            session.commit()
            session.close()

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Error occurred: {e}")

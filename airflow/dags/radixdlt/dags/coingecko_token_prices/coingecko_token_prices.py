import logging
from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config
from radixdlt.models.coingecko_api.token_prices import CoinGeckoTokenData


logging.basicConfig(level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 8, 21),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="coingecko_token_prices",
    default_args=default_args,
    description="DAG to fetch token prices from coingecko",
    schedule_interval=Config.COINGECKO_TOKEN_PRICES_SCHEDULE_INTERVAL,
    catchup=False,
)
def coingecko_prices():
    @task
    def fetch_coingecko_prices(token):
        CoinGeckoTokenData.fetch_and_save_data(token)

    # Looping on the task level provides individual tasks and their status. Failed task can be tried specifically instead of running all of them
    for token in Config.COINGECKO_TOKENS.split(","):
        fetch_coingecko_prices(token)


coingecko_prices()

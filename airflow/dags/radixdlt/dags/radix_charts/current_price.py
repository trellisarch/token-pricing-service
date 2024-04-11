import logging

from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config
from radixdlt.models.radix_charts.token import RadixToken
from radixdlt.models.radix_charts.token_price import RadixTokenPrice

logging.basicConfig(level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="radix_charts_current_price",
    default_args=default_args,
    description="DAG to fetch tokens price and save to PostgreSQL",
    schedule_interval=Config.TOKEN_PRICE_SCHEDULE_INTERVAL,
    catchup=False,
)
def radix_charts_prices():
    @task
    def fetch_tokens_price_task():
        tokens = RadixToken.list_tokens()
        RadixTokenPrice.fetch_and_save_prices(tokens)

    fetch_tokens_price_task()


radix_charts_prices()

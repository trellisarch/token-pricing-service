import logging
from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config
from radixdlt.lib.const import LEDGER_TOKENS
from radixdlt.models.ledger_prices.token_price import LedgerPriceFetcher

logging.basicConfig(level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="ledger_current_price",
    default_args=default_args,
    description="DAG to fetch token prices from Radix ledger DEX pools and save to PostgreSQL",
    schedule_interval=Config.LEDGER_PRICE_SCHEDULE_INTERVAL,
    catchup=False,
)
def ledger_prices():
    @task
    def fetch_prices_task():
        LedgerPriceFetcher.fetch_and_save_prices(LEDGER_TOKENS)

    fetch_prices_task()


ledger_prices()

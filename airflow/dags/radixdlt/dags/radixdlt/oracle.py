from datetime import datetime, timedelta
from airflow.decorators import task, dag
from radixdlt.lib.cmc import process_cmc_prices
from radixdlt.lib.coingecko import process_coin_gecko_prices
from radixdlt.lib.oracle import update_oracle
from radixdlt.lib.pyth import process_pyth_prices

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    schedule_interval="*/1 * * * *",
    default_args=default_args,
    catchup=False,
    dag_id="oracle_price",
)
def oracle_prices_dag():

    @task
    def process_coin_gecko_prices_task():
        return process_coin_gecko_prices()

    @task
    def process_cmc_prices_task():
        return process_cmc_prices()

    @task
    def process_pyth_prices_task():
        return process_pyth_prices()

    @task
    def update_oracle_task(coin_gecko_prices, cmc_prices, pyth_prices):
        update_oracle(coin_gecko_prices, cmc_prices, pyth_prices)

    update_oracle_task(
        process_coin_gecko_prices_task(),
        process_cmc_prices_task(),
        process_pyth_prices_task(),
    )


oracle_prices_dag()

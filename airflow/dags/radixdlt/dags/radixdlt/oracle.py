import logging
from datetime import datetime
from airflow import AirflowException
from airflow.decorators import task, dag
from radixdlt.config.config import Config
from radixdlt.lib.cmc import process_cmc_prices
from radixdlt.lib.coingecko import process_coin_gecko_prices
from radixdlt.lib.gateway import is_transaction_committed
from radixdlt.lib.oracle import update_oracle
from radixdlt.lib.pyth import process_pyth_prices

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
}


@dag(
    schedule_interval=Config.ORACLE_SCHEDULE_INTERVAL,
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
        if coin_gecko_prices == {} and cmc_prices == {}:
            raise AirflowException("Both Gecko and CMC prices are empty")
        return update_oracle(coin_gecko_prices, cmc_prices, pyth_prices)

    @task
    def get_transaction_status_task(txn_intent_hash):
        logging.info(f"Getting the status of transaction: {txn_intent_hash}")
        transaction_committed = is_transaction_committed(txn_intent_hash)
        assert transaction_committed

    get_transaction_status_task(
        update_oracle_task(
            process_coin_gecko_prices_task(),
            process_cmc_prices_task(),
            process_pyth_prices_task(),
        )
    )


oracle_prices_dag()

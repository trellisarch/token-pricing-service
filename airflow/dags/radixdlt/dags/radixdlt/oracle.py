import logging
from datetime import datetime
from airflow import AirflowException
from airflow.decorators import task, dag
from radixdlt.config.config import Config
from radixdlt.lib.c9 import process_c9_prices
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
    def process_c9_prices_task():
        return process_c9_prices()

    @task
    def update_oracle_task(coin_gecko_prices, cmc_prices, pyth_prices, c9_prices):
        if coin_gecko_prices == {} and cmc_prices == {}:
            raise AirflowException("Both Gecko and CMC prices are empty")
        return update_oracle(coin_gecko_prices, cmc_prices, pyth_prices, c9_prices)

    @task
    def get_transaction_status_task(transaction_metadata):
        logging.info(
            f"Getting the status of transaction: {transaction_metadata['txn_intent_hash']}"
        )
        transaction_committed = is_transaction_committed(
            transaction_metadata["txn_intent_hash"]
        )
        assert transaction_committed
        return transaction_metadata

    @task
    def assert_all_pairs_updated_task(transaction_metadata):
        logging.info(transaction_metadata)
        # asserting that all CMC pairs are updated and c9 too
        # TODO: add a better way to do this assertion
        assert len(transaction_metadata["transactions"]) == len(
            Config.ORACLE_CMC_PAIRS.split(",") + 1
        )

    assert_all_pairs_updated_task(
        get_transaction_status_task(
            update_oracle_task(
                process_coin_gecko_prices_task(),
                process_cmc_prices_task(),
                process_pyth_prices_task(),
                process_c9_prices_task(),
            )
        )
    )


oracle_prices_dag()

import logging
from datetime import datetime
from airflow.dags.radixdlt.lib.cmc import CmcPriceProvider
from airflow.decorators import task, dag
from radixdlt.config.config import Config
from radixdlt.lib.c9 import C9PriceProvider
from radixdlt.lib.gateway import is_transaction_committed
from radixdlt.lib.oracle import OracleUpdater
from radixdlt.lib.pyth import PythPriceProvider
from radixdlt.lib.radix_charts import RadixChartsPriceProvider

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
    def process_cmc_prices_task():
        cmc_price_provider = CmcPriceProvider()
        cmc_price_provider.process_prices()
        return cmc_price_provider.prices

    @task
    def process_c9_prices_task():
        c9_price_provider = C9PriceProvider()
        c9_price_provider.process_prices()
        return c9_price_provider.prices

    @task
    def process_radix_charts_prices_task():
        radix_charts_price_provider = RadixChartsPriceProvider()
        radix_charts_price_provider.process_prices()
        return radix_charts_price_provider.prices

    @task
    def update_oracle_task(cmc_prices, c9_prices, radix_charts_pricess):
        oracle_updater = OracleUpdater()
        return oracle_updater.update_prices(cmc_prices, c9_prices, radix_charts_pricess)

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
    def add_metrics_all_pairs_updated_task(transaction_metadata):
        logging.info(transaction_metadata)
        oracle_updater = OracleUpdater()
        oracle_updater.check_add_missing_quotes(transaction_metadata)

    add_metrics_all_pairs_updated_task(
        get_transaction_status_task(
            update_oracle_task(
                process_cmc_prices_task(),
                process_c9_prices_task(),
                process_radix_charts_prices_task(),
            )
        )
    )


oracle_prices_dag()

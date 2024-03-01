import asyncio
from datetime import datetime, timedelta
from airflow.decorators import task, dag
from radixdlt.lib.cmc import process_cmc_prices
from radixdlt.lib.coingecko import calculate_xrd_quote, process_coin_gecko_prices
from radixdlt.lib.oracle import update_oracle
from radixdlt.lib.pyth import get_pyth_prices


from radixdlt.models.oracles.token_price import OracleTokenPrice

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(schedule=None, default_args=default_args, catchup=False, dag_id="oracle_price")
def oracle_prices_dag():

    @task
    def process_coin_gecko_prices_task():
        return process_coin_gecko_prices()

    @task
    def process_cmc_prices_task():
        return process_cmc_prices()

    @task
    def process_pyth_prices_task():
        pyth_xrd_prices = {}
        pyth_prices = asyncio.run(get_pyth_prices())
        for pair in pyth_prices.keys():
            pyth_xrd_price = calculate_xrd_quote(
                pyth_prices[pair], pyth_prices["XRD/USD"]
            )
            pyth_xrd_prices[f'{pair.split("/")[0]}/XRD'] = pyth_xrd_price
            OracleTokenPrice.insert_price(pair, pyth_xrd_price, "PYTH")
        return pyth_xrd_prices

    @task
    def update_oracle_task(coin_gecko_prices, cmc_prices, pyth_prices):
        update_oracle(coin_gecko_prices, cmc_prices, pyth_prices)

    update_oracle(
        process_coin_gecko_prices_task(),
        process_cmc_prices_task(),
        process_pyth_prices_task(),
    )


oracle_prices_dag()

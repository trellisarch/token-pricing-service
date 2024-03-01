import asyncio
import logging
from datetime import datetime, timedelta
import requests
from airflow.decorators import task, dag
from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key

from radixdlt.config.config import Config
from radixdlt.lib.coingecko import calculate_xrd_quote, process_coin_gecko_prices
from radixdlt.lib.ret import create_transaction

from radixdlt.models.oracles.token_price import OracleTokenPrice

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


async def get_pyth_prices():
    v2_first_mapping_account_key = get_key("pythnet", "mapping")
    v2_program_key = get_key("pythnet", "program")
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key,
        solana_endpoint=PYTHNET_HTTP_ENDPOINT,
    ) as c:
        pyth_prices = {}
        products = await c.get_products()
        for p in products:
            if p.symbol in [
                "Crypto.BTC/USD",
                "Crypto.XRD/USD",
                "Crypto.ETH/USD",
                "Crypto.USDT/USD",
                "Crypto.USDC/USD",
            ]:

                prices = await p.get_prices()
                for _, pr in prices.items():
                    pyth_prices[p.symbol.split("Crypto.")[1]] = pr.aggregate_price
        await c.close()
        return pyth_prices


@dag(schedule=None, default_args=default_args, catchup=False, dag_id="oracle_price")
def oracle_prices_dag():

    @task
    def process_coin_gecko_prices_task():
        return process_coin_gecko_prices()

    @task
    def process_cmc_pairs():
        pairs = Config.ORACLE_CMC_PAIRS.split(",")
        cmc_prices = {}
        # TODO once we have a better plan at CMC we can avoid this for loop
        for pair in pairs:
            logging.info(f"Getting price for pair: {pair}")
            base = pair.split("/")[0]
            quote = pair.split("/")[1]
            url = (
                f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/"
                f"quotes/latest?symbol={base}&convert={quote}"
            )
            headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": f"{Config.COINMARKETCAP_DEV_API_KEY}",
            }
            cmc_price_response = requests.get(url=url, headers=headers)
            if cmc_price_response.status_code == 200:
                cmc_price = cmc_price_response.json()["data"][base][0]["quote"][quote][
                    "price"
                ]
                cmc_prices[pair] = cmc_price
                OracleTokenPrice.insert_price(pair, cmc_price, "CMC")
            else:
                logging.info(cmc_price_response.text)
        return cmc_prices

    @task
    def process_pyth_prices():
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
    def update_oracle(coin_gecko_prices, cmc_prices, pyth_prices):
        transaction_metadata = []
        logging.info(f"Gecko prices: {coin_gecko_prices}")
        logging.info(f"CMC prices: {cmc_prices}")
        logging.info(f"Pyth prices: {pyth_prices}")
        for pair, gecko_price in coin_gecko_prices.items():
            cmc_price = cmc_prices.get(pair, None)
            if cmc_price is not None:
                logging.info(f"Checking pair: {pair}")
                logging.info(f"Gecko price: {gecko_price}")
                logging.info(f"CMC price: {cmc_price}")
                logging.info(f"PYTH price: {pyth_prices[pair]}")

                gecko_lowest_price = gecko_price - gecko_price * 5 / 100
                gecko_highest_price = gecko_price + gecko_price * 5 / 100

                cmc_lowest_price = cmc_price - cmc_price * 5 / 100
                cmc_highest_price = cmc_price + cmc_price * 5 / 100

                if (gecko_lowest_price < pyth_prices[pair] < gecko_highest_price) or (
                    cmc_lowest_price < pyth_prices[pair] < cmc_highest_price
                ):
                    transaction_metadata.append(
                        {"base": pair.split("/")[0], "price": pyth_prices[pair]}
                    )
        if len(transaction_metadata) > 0:
            logging.info(transaction_metadata)
            notarized_transaction_hex, address = create_transaction(
                transaction_metadata
            )
            submit_transaction_body = {
                "notarized_transaction_hex": notarized_transaction_hex
            }
            requests.post(
                url=f"{Config.NETWORK_GATEWAY}/transaction/submit",
                json=submit_transaction_body,
            )
        else:
            logging.info("Nothing to update")

    update_oracle(
        process_coin_gecko_prices(), process_cmc_pairs(), process_pyth_prices()
    )


oracle_prices_dag()

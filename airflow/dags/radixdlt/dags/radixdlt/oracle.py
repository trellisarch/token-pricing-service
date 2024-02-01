import logging
from datetime import datetime, timedelta
import requests
from airflow.decorators import task, dag
from radixdlt.config.config import Config
from radixdlt.lib.coingecko import calculate_xrd_quote
from radixdlt.lib.ret import create_transaction

from radixdlt.models.oracles.token_price import OracleTokenPrice

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

COIN_DICT = {
    "radix": "XRD",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "usd-coin": "USDC",
}


@dag(schedule=None, default_args=default_args, catchup=False, dag_id="oracle_price")
def oracle_prices_dag():

    @task
    def process_coin_gecko_prices():
        headers = {"accept": "application/json"}
        coin_ids = Config.ORACLE_COIN_GECKO_IDS.split(",")

        coin_gecko_price = requests.get(
            url=f"{Config.COIN_GECKO_API}/simple/price?ids="
            f"{','.join(coin_ids)},radix&vs_currencies=USD",
            headers=headers,
        ).json()

        coin_gecko_prices = {}
        for coin_id in coin_ids:
            coin_pair = f"{COIN_DICT[coin_id]}/XRD"
            coin_gecko_xrd_price = calculate_xrd_quote(
                coin_gecko_price[coin_id]["usd"], coin_gecko_price["radix"]["usd"]
            )
            coin_gecko_prices[coin_pair] = coin_gecko_xrd_price
            OracleTokenPrice.insert_price(coin_pair, coin_gecko_xrd_price, "CoinGecko")
        return coin_gecko_prices

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

            logging.info(headers)
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
    def update_oracle(coin_gecko_prices, cmc_prices):
        transaction_metadata = []
        for pair, gecko_price in coin_gecko_prices.items():
            cmc_price = cmc_prices.get(pair, None)
            if cmc_price is not None:
                logging.info(f"Checking pair: {pair}")
                logging.info(f"Gecko price: {gecko_price}")
                logging.info(f"CMC price: {cmc_price}")
                price_diff = abs(gecko_price - cmc_price) / max(gecko_price, cmc_price)
                logging.info(f"Price difference: {price_diff}")
                if price_diff < Config.ORACLE_PRICE_DIFF_TRIGGER:
                    avg_price = (gecko_price + cmc_price) / 2
                    transaction_metadata.append(
                        {"base": pair.split("/")[0], "price": avg_price}
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

    update_oracle(process_coin_gecko_prices(), process_cmc_pairs())


oracle_prices_dag()

from datetime import datetime, timedelta
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator
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

dag = DAG(
    "oracle_prices",
    default_args=default_args,
    description="DAG to fetch quotes from CMC and Coin Gecko",
    schedule_interval=None,
)


def process_quotes():
    headers = {"accept": "application/json"}

    coin_gecko_prices = {}
    coin_gecko_price = requests.get(
        url=f"https://api.coingecko.com/api/v3/simple/price?ids="
        f"radix,bitcoin,ethereum,tether,usd-coin&vs_currencies=USD",
        headers=headers,
    ).json()

    coin_gecko_btc_xrd_price = calculate_xrd_quote(
        coin_gecko_price["bitcoin"]["usd"], coin_gecko_price["radix"]["usd"]
    )
    coin_gecko_prices["BTC/XRD"] = coin_gecko_btc_xrd_price
    OracleTokenPrice.insert_price("BTC/XRD", coin_gecko_btc_xrd_price, "CoinGecko")

    coin_gecko_eth_xrd_price = calculate_xrd_quote(
        coin_gecko_price["ethereum"]["usd"], coin_gecko_price["radix"]["usd"]
    )
    coin_gecko_prices["ETH/XRD"] = coin_gecko_eth_xrd_price
    OracleTokenPrice.insert_price("ETH/XRD", coin_gecko_eth_xrd_price, "CoinGecko")

    coin_gecko_usdt_xrd_price = calculate_xrd_quote(
        coin_gecko_price["tether"]["usd"], coin_gecko_price["radix"]["usd"]
    )
    coin_gecko_prices["USDT/XRD"] = coin_gecko_usdt_xrd_price
    OracleTokenPrice.insert_price("USDT/XRD", coin_gecko_usdt_xrd_price, "CoinGecko")

    coin_gecko_usdc_xrd_price = calculate_xrd_quote(
        coin_gecko_price["usd-coin"]["usd"], coin_gecko_price["radix"]["usd"]
    )
    coin_gecko_prices["USDC/XRD"] = coin_gecko_usdc_xrd_price
    OracleTokenPrice.insert_price("USDC/XRD", coin_gecko_usdc_xrd_price, "CoinGecko")

    pairs = ["BTC/XRD", "ETH/XRD", "USDT/XRD", "USDC/XRD"]
    cmc_prices = {}
    for pair in pairs:
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

        cmc_price = requests.get(url=url, headers=headers).json()["data"][base][0][
            "quote"
        ][quote]["price"]
        cmc_prices[pair] = cmc_price
        OracleTokenPrice.insert_price(pair, cmc_price, "CMC")

    # TODO this is hardcoded now but we need to create the list based on the price diff
    base_symbols = ["BTC", "USDT"]
    notarized_transaction_hex, address = create_transaction(base_symbols)
    submit_transaction_body = {"notarized_transaction_hex": notarized_transaction_hex}
    requests.post(url=Config.NETWORK_GATEWAY, json=submit_transaction_body)


process_quotes_task = PythonOperator(
    task_id="process_quotes",
    python_callable=process_quotes,
    dag=dag,
)

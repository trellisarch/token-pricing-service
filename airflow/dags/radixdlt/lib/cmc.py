import logging

import requests

from radixdlt.config.config import Config
from radixdlt.models.oracles.token_price import OracleTokenPrice


def process_cmc_prices():
    pairs = Config.ORACLE_CMC_PAIRS.split(",")
    cmc_prices = {}

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
            raise Exception("Failed to get CMC prices")

    return cmc_prices

import logging
from datetime import datetime

import requests

from radixdlt.config.config import Config
from radixdlt.models.oracles.token_price import OracleTokenPrice


def process_cmc_prices():
    utc_now_seconds = int(datetime.utcnow().timestamp())
    utc_three_minutes_ago = utc_now_seconds - Config.STALE_PERIOD_SECS

    pairs = Config.ORACLE_CMC_PAIRS.split(",")
    quote_pairs = ",".join([pair.split("/")[0] for pair in pairs])
    cmc_prices = {}
    logging.info(f"Getting price for pairs: {quote_pairs}")
    url = (
        f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/"
        f"quotes/latest?symbol={quote_pairs}&convert={Config.RADIX_TOKEN}"
    )
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": f"{Config.COINMARKETCAP_DEV_API_KEY}",
    }
    try:
        cmc_price_response = requests.get(url=url, headers=headers)
        if cmc_price_response.status_code == 200:
            logging.info(cmc_price_response.json())
            pairs_prices = cmc_price_response.json()["data"]
            for key in pairs_prices.keys():
                pair = f"{key}/{Config.RADIX_TOKEN}"

                cmc_price = pairs_prices[key][0]["quote"][Config.RADIX_TOKEN]["price"]
                last_updated_date = datetime.strptime(
                    pairs_prices[key][0]["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                last_updated_seconds = int(last_updated_date.timestamp())
                if last_updated_seconds > utc_three_minutes_ago:
                    cmc_prices[pair] = cmc_price
                    OracleTokenPrice.insert_price(pair, cmc_price, "CMC")
        else:
            logging.info(cmc_price_response.text)
            raise Exception("Failed to get CMC prices")
    except Exception as e:
        logging.info(str(e))
    logging.info(f"CMC prices: {cmc_prices}")
    return cmc_prices

import logging
from datetime import datetime

import requests
from radixdlt.config.config import Config
from radixdlt.models.oracles.source_price import OracleSourcePrice
from radixdlt.models.oracles.token_price import OracleTokenPrice

COIN_DICT = {
    "radix": "XRD",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "usd-coin": "USDC",
}


def calculate_xrd_quote(base_usd_price, xrd_usd_price):
    return base_usd_price / xrd_usd_price


def process_coin_gecko_prices():
    utc_now_seconds = int(datetime.utcnow().timestamp())
    coin_gecko_prices = {}
    headers = {
        "accept": "application/json",
        "x-cg-pro-api-key": Config.COIN_GECKO_API_KEY,
    }
    coin_ids = Config.ORACLE_COIN_GECKO_IDS.split(",")

    try:
        logging.info(f"Getting gecko prices from {Config.COIN_GECKO_API}")
        coin_gecko_price_response = requests.get(
            url=f"{Config.COIN_GECKO_API}/simple/price?ids="
            f"{','.join(coin_ids)},radix&vs_currencies=USD&include_last_updated_at=true",
            headers=headers,
        )
        if coin_gecko_price_response.status_code == 200:
            coin_gecko_price = coin_gecko_price_response.json()
            logging.info(coin_gecko_price)
        else:
            logging.info(coin_gecko_price_response.text)
            raise

        for coin_id in coin_ids:
            if coin_id != "radix":
                coin_pair = f"{COIN_DICT[coin_id]}/XRD"
                last_updated_seconds = coin_gecko_price[coin_id]["last_updated_at"]
                last_updated = utc_now_seconds - last_updated_seconds
                logging.info(f"Current time: {utc_now_seconds}")
                logging.info(f"Last updated time: {last_updated_seconds}")
                logging.info(f"Pair {coin_pair} updated {last_updated} seconds ago")

                coin_pair = f"{COIN_DICT[coin_id]}/XRD"
                coin_gecko_xrd_price = calculate_xrd_quote(
                    coin_gecko_price[coin_id]["usd"], coin_gecko_price["radix"]["usd"]
                )
                if coin_pair in Config.STALE_CHECK_PAIRS:
                    logging.info(f"Checking pair: {coin_pair} is not stale")
                    if last_updated < Config.STALE_PERIOD_SECS:
                        logging.info(
                            f"Pair: {coin_pair} updated {last_updated} seconds ago, not stale"
                        )
                        coin_gecko_prices[coin_pair] = coin_gecko_xrd_price
                    else:
                        logging.info(
                            f"Pair: {coin_pair} updated {last_updated} seconds ago, stale"
                        )
                else:
                    logging.info(f"Skipping stale check for pair: {coin_pair}")
                    coin_gecko_prices[coin_pair] = coin_gecko_xrd_price
                OracleSourcePrice.insert_source_price(
                    pair=coin_pair,
                    quote=coin_gecko_xrd_price,
                    quote_source="Gecko",
                    last_updated=last_updated,
                )
    except Exception as e:
        logging.info(str(e))
    logging.info(f"Gecko prices: {coin_gecko_prices}")
    return coin_gecko_prices

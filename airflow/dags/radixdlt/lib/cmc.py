import logging
from datetime import datetime
import requests
from radixdlt.config.config import Config
from radixdlt.lib.price_provider import BasePriceProvider


class CmcPriceProvider(BasePriceProvider):

    def __init__(self):
        # The self.prices dictionary will have the following structure:
        # {
        #     "PAIR_NAME": PRICE_VALUE,
        #     ...
        # }
        # Example:
        # {
        #     "BTC/XRD": 12345.67,
        #     "ETH/XRD": 2345.89,
        # }
        self.prices = {} 

    def process_prices(self):
        utc_now_seconds = int(datetime.utcnow().timestamp())
        pairs = Config.ORACLE_CMC_PAIRS.split(",")
        quote_pairs = ",".join([pair.split("/")[0] for pair in pairs])
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

                    cmc_price = pairs_prices[key][0]["quote"][Config.RADIX_TOKEN][
                        "price"
                    ]
                    last_updated_date = datetime.strptime(
                        pairs_prices[key][0]["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    last_updated_seconds = int(last_updated_date.timestamp())
                    last_updated = utc_now_seconds - last_updated_seconds
                    logging.info(f"Current time: {utc_now_seconds}")
                    logging.info(f"Last updated time: {last_updated_seconds}")
                    logging.info(f"Pair {pair} updated {last_updated} seconds ago")
                    if pair in Config.STALE_CHECK_PAIRS:
                        logging.info(f"Checking pair: {pair} is not stale")
                        if last_updated < Config.STALE_PERIOD_SECS:
                            logging.info(
                                f"Pair: {pair} updated {last_updated} seconds ago, not stale"
                            )
                            self.prices[pair] = cmc_price
                        else:
                            logging.info(
                                f"Pair: {pair} updated {last_updated} seconds ago, stale"
                            )
                    else:
                        logging.info(f"Skipping stale check for pair: {pair}")
                        self.prices[pair] = cmc_price
            else:
                logging.info(cmc_price_response.text)
                raise Exception("Failed to get CMC prices")
        except Exception as e:
            logging.info(str(e))
        logging.info(f"CMC prices: {self.prices}")

def get_quotes(prices) -> list:   
    quotes = []
    for pair, price in prices.items():
        base = pair.split("/")[0]
        quotes.append({"base": base, "price": price})
    return quotes
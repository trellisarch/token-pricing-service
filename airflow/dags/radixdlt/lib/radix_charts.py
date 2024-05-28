import logging
import requests
from radixdlt.config.config import Config
from radixdlt.lib.coingecko import GeckoPriceProvider
from radixdlt.lib.const import RADIX_CHARTS_TOKENS
from radixdlt.lib.http import get_radix_charts_headers
from radixdlt.lib.price_provider import BasePriceProvider


class RadixChartsPriceProvider(BasePriceProvider):

    def __init__(self):
        self.prices = {}

    def process_prices(self):
        try:
            current_price_endpoint = Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT
            resources_names = Config.RADIX_CHARTS_ORACLE_TOKENS.split(",")
            resources_addresses = ",".join(
                RADIX_CHARTS_TOKENS[name]["resource_address"]
                for name in resources_names
            )
            params = {"resource_addresses": resources_addresses}
            logging.info(params)
            charts_prices = requests.get(
                url=current_price_endpoint,
                params=params,
                headers=get_radix_charts_headers(),
            ).json()["data"]

            for resource_address in charts_prices:
                if charts_prices[resource_address]["symbol"] != "$XRD":
                    usd_price = charts_prices[resource_address]["usd_price"]
                    xrd_price = charts_prices[
                        RADIX_CHARTS_TOKENS["radix"]["resource_address"]
                    ]["usd_price"]
                    self.prices[f'{charts_prices[resource_address]["symbol"]}/XRD'] = (
                        usd_price / xrd_price
                    )
            logging.info(self.prices)
        except Exception:
            raise


def validate_prices(prices):
    valid_quotes = []
    coin_gecko_price_provider = GeckoPriceProvider()
    coin_gecko_price_provider.process_prices()
    logging.info(prices)
    logging.info(coin_gecko_price_provider.prices)
    for pair, quote in prices.items():
        logging.info(f"{pair}: {quote}")
        logging.info(f'{pair}: {coin_gecko_price_provider.prices[f"{pair}"]}')
        gecko_lowest_price = (
            coin_gecko_price_provider.prices[f"{pair}"]
            - coin_gecko_price_provider.prices[f"{pair}"]
            * Config.ORACLE_PRICE_DIFF_TRIGGER
        )
        gecko_highest_price = (
            coin_gecko_price_provider.prices[f"{pair}"]
            + coin_gecko_price_provider.prices[f"{pair}"]
            * Config.ORACLE_PRICE_DIFF_TRIGGER
        )
        if gecko_lowest_price < quote < gecko_highest_price:
            logging.info(f"Gecko lower limit: {gecko_lowest_price}")
            logging.info(f"Gecko higher limit: {gecko_highest_price}")
            logging.info(f"Charts price: {quote}")
            valid_quotes.append({"base": pair.split("/")[0], "price": quote})
    logging.info(f"radix charts quotes: {valid_quotes}")
    return valid_quotes

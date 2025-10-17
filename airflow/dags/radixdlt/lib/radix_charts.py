import logging
import time
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
        start_time = time.time()
        try:
            current_price_endpoint = Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT
            resources_names = Config.RADIX_CHARTS_ORACLE_TOKENS.split(",")
            resources_addresses = ",".join(
                RADIX_CHARTS_TOKENS[name]["resource_address"]
                for name in resources_names
            )
            params = {"resource_addresses": resources_addresses}
            logging.info(params)
            response = requests.get(
                url=current_price_endpoint,
                params=params,
                headers=get_radix_charts_headers(),
            )
            duration = (time.time() - start_time) * 1000  # convert to milliseconds
            Config.statsDClient.timing("oracle.radixcharts.request_time", duration)

            if response.status_code not in (200, 204):
                Config.statsDClient.incr("dag_oracle.radixchart.failed")
                logging.error(
                    f"Radixchart API failed with status code: {response.status_code}"
                )
                logging.error(f"Request URL: {current_price_endpoint}")
                logging.error(f"Request params: {params}")
                logging.error(f"Response headers: {dict(response.headers)}")
                logging.error(f"Response content: {response.text}")
                raise Exception(
                    f"Radixchart returned error: HTTP {response.status_code}"
                )

            Config.statsDClient.incr("dag_oracle.radixchart.passed")
            charts_prices = response.json()["data"]

            add_statsd_metrics(charts_prices)

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
        except Exception as e:
            # Increment the failure counter
            Config.statsDClient.incr("dag_oracle.radixchart.failed")
            logging.error(f"Error fetching data from external service radixchart: {e}")
            logging.exception("Full exception details:")
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


def add_statsd_metrics(radixchart_response):

    for key, value in RADIX_CHARTS_TOKENS.items():
        resource_address = value["resource_address"]
        symbol = value["symbol"]

        # Skip if symbol is "XRD"
        if symbol == "XRD":
            continue

        found = False
        for item in radixchart_response:
            if resource_address in item:
                found = True
                break
        symbol_fixed = symbol.replace("$", "")

        # If the resource_address is not found, increment the metric
        if not found:
            print(
                f"No price returned for {key}: {symbol} (Resource Address: {resource_address})"
            )
            Config.statsDClient.incr(
                f"dag_oracle.radixchart.fetch.{symbol_fixed}.failed"
            )
        else:
            Config.statsDClient.incr(
                f"dag_oracle.radixchart.fetch.{symbol_fixed}.passed"
            )

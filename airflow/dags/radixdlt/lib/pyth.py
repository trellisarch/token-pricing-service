import asyncio
import logging
from datetime import datetime, timezone
from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key

from radixdlt.config.config import Config
from radixdlt.lib.cmc import CmcPriceProvider
from radixdlt.lib.coingecko import GeckoPriceProvider
from radixdlt.lib.price_provider import BasePriceProvider


class PythPriceProvider(BasePriceProvider):

    def __init__(self):
        self.prices = {}

    @staticmethod
    async def get_pyth_prices():
        utc_now_seconds = int(datetime.now(timezone.utc).timestamp())
        utc_one_minutes_ago = utc_now_seconds - 60
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
                    pair = p.symbol.split("Crypto.")[1]
                    pyth_prices[pair] = {}
                    prices = await p.get_prices()
                    for _, pr in prices.items():
                        if pr.timestamp > utc_one_minutes_ago:
                            pyth_prices[pair]["price"] = pr.aggregate_price
                            pyth_prices[pair]["last_updated_at"] = pr.timestamp

            await c.close()
            return pyth_prices

    def process_prices(self):
        try:
            pyth_prices = asyncio.run(self.get_pyth_prices())
            for pair in pyth_prices.keys():
                logging.info(f"Pyth pair: {pair}")
                if pair != "XRD/USD":
                    pyth_xrd_price = (
                        pyth_prices[pair]["price"] / pyth_prices["XRD/USD"]["price"]
                    )
                    self.prices[f'{pair.split("/")[0]}/XRD'] = pyth_xrd_price
        except Exception:
            raise


def validate_prices(prices):
    valid_quotes = []
    cmc_price_provider = CmcPriceProvider()
    cmc_price_provider.process_prices()
    coin_gecko_price_provider = GeckoPriceProvider()
    coin_gecko_price_provider.process_prices()

    for pair, pyth_price in prices.items():
        cmc_price = cmc_price_provider.prices.get(pair, None)
        gecko_price = coin_gecko_price_provider.prices.get(pair, None)

        if cmc_price is None and gecko_price is None:
            logging.info(f"Both gecko and cmc prices for {pair} are None")
        else:
            logging.info(f"Checking pair: {pair}")
            logging.info(f"Gecko price: {gecko_price}")
            logging.info(f"CMC price: {cmc_price}")
            logging.info(f"PYTH price: {prices[pair]}")

            logging.info("Using CMC price as primary source. Using CMC to compare pyth")
            if cmc_price is not None:
                cmc_lowest_price = (
                    cmc_price - cmc_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                )
                cmc_highest_price = (
                    cmc_price + cmc_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                )
                if cmc_lowest_price < prices[pair] < cmc_highest_price:
                    logging.info(f"CMC lower limit: {cmc_lowest_price}")
                    logging.info(f"CMC higher limit: {cmc_highest_price}")
                    logging.info(f"Pyth price: {pyth_price}")
                    valid_quotes.append(
                        {"base": pair.split("/")[0], "price": prices[pair]}
                    )
            else:
                if gecko_price is not None:
                    logging.info("CMC price is None. using Gecko instead")
                    gecko_lowest_price = (
                        gecko_price - gecko_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                    )
                    gecko_highest_price = (
                        gecko_price + gecko_price * Config.ORACLE_PRICE_DIFF_TRIGGER
                    )
                    if gecko_lowest_price < prices[pair] < gecko_highest_price:
                        logging.info(f"Gecko lower limit: {gecko_lowest_price}")
                        logging.info(f"Gecko higher limit: {gecko_highest_price}")
                        logging.info(f"Pyth price: {pyth_price}")
                        valid_quotes.append(
                            {"base": pair.split("/")[0], "price": prices[pair]}
                        )
    logging.info(f"PYTH quotes: {valid_quotes}")
    return valid_quotes

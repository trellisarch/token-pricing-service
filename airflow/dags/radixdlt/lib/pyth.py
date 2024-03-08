import asyncio
import logging
from datetime import datetime

from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key

from radixdlt.lib.coingecko import calculate_xrd_quote
from radixdlt.models.oracles.token_price import OracleTokenPrice


async def get_pyth_prices():
    utc_now_seconds = int(datetime.utcnow().timestamp())
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
                prices = await p.get_prices()
                for _, pr in prices.items():
                    if pr.timestamp > utc_one_minutes_ago:
                        pyth_prices[p.symbol.split("Crypto.")[1]] = pr.aggregate_price
        await c.close()
        return pyth_prices


def process_pyth_prices():
    pyth_xrd_prices = {}
    try:
        pyth_prices = asyncio.run(get_pyth_prices())
        for pair in pyth_prices.keys():
            logging.info(f"Pyth pair: {pair}")
            if pair != "XRD/USD":
                pyth_xrd_price = calculate_xrd_quote(
                    pyth_prices[pair], pyth_prices["XRD/USD"]
                )
                pyth_xrd_prices[f'{pair.split("/")[0]}/XRD'] = pyth_xrd_price
                OracleTokenPrice.insert_price(pair, pyth_xrd_price, "PYTH")
    except Exception:
        raise
    return pyth_xrd_prices

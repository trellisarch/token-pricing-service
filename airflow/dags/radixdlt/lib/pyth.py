import asyncio

from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key

from radixdlt.lib.coingecko import calculate_xrd_quote
from radixdlt.models.oracles.token_price import OracleTokenPrice


async def get_pyth_prices():
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
                    pyth_prices[p.symbol.split("Crypto.")[1]] = pr.aggregate_price
        await c.close()
        return pyth_prices


def process_pyth_prices():
    pyth_xrd_prices = {}
    pyth_prices = asyncio.run(get_pyth_prices())
    for pair in pyth_prices.keys():
        pyth_xrd_price = calculate_xrd_quote(pyth_prices[pair], pyth_prices["XRD/USD"])
        pyth_xrd_prices[f'{pair.split("/")[0]}/XRD'] = pyth_xrd_price
        OracleTokenPrice.insert_price(pair, pyth_xrd_price, "PYTH")
    return pyth_xrd_prices

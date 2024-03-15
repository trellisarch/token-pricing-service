import asyncio
import logging
from datetime import datetime, timezone

from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key

from radixdlt.lib.coingecko import calculate_xrd_quote
from radixdlt.models.oracles.source_price import OracleSourcePrice
from radixdlt.models.oracles.token_price import OracleTokenPrice


async def get_pyth_prices():
    utc_now_seconds = int(datetime.now(timezone.utc).timestamp())
    utc_one_minutes_ago = utc_now_seconds - 120
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


def process_pyth_prices():
    pyth_xrd_prices = {}
    utc_now_seconds = int(datetime.utcnow().timestamp())
    try:
        pyth_prices = asyncio.run(get_pyth_prices())
        for pair in pyth_prices.keys():
            logging.info(f"Pyth pair: {pair}")
            if pair != "XRD/USD":
                pyth_xrd_price = calculate_xrd_quote(
                    pyth_prices[pair]["price"], pyth_prices["XRD/USD"]["price"]
                )
                pyth_xrd_prices[f'{pair.split("/")[0]}/XRD'] = pyth_xrd_price
                OracleSourcePrice.insert_source_price(
                    pair=pair,
                    quote=pyth_xrd_price,
                    quote_source="PYTH",
                    last_updated=utc_now_seconds - pyth_prices[pair]["last_updated_at"],
                )
    except Exception:
        raise
    return pyth_xrd_prices

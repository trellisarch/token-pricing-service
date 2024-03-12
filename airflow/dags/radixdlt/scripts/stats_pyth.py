import asyncio
import logging
from datetime import datetime
from time import sleep
import pandas as pd
import requests
from pythclient.pythclient import PythClient
from pythclient.solana import PYTHNET_HTTP_ENDPOINT
from pythclient.utils import get_key


async def get_pyth_prices():
    v2_first_mapping_account_key = get_key("pythnet", "mapping")
    v2_program_key = get_key("pythnet", "program")
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key,
        solana_endpoint=PYTHNET_HTTP_ENDPOINT,
    ) as c:
        pyth_prices = []
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
                    pyth_prices.append(pr)
        await c.close()
        return pyth_prices


if __name__ == "__main__":
    prices = []
    for i in range(60):
        print(f"Getting prices from Pyth: {i}")
        pyth_prices = asyncio.run(get_pyth_prices())
        utc_now_seconds = int(datetime.utcnow().timestamp())
        for price in pyth_prices:
            prices.append(
                [
                    i,
                    "PYTH",
                    price.product.symbol,
                    price.aggregate_price,
                    utc_now_seconds - price.timestamp,
                ]
            )
        sleep(60)
    df = pd.DataFrame(prices)
    csv_file_path = "output_pyth.csv"
    df.to_csv(csv_file_path, index=False, header=False)
    print(prices)

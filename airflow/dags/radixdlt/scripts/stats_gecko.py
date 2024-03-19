from datetime import datetime, timezone
from time import sleep
import pandas as pd
import requests


COIN_DICT = {
    "radix": "XRD",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "usd-coin": "USDC",
}

if __name__ == "__main__":
    coin_gecko_prices = {}
    headers = {
        "accept": "application/json",
        "x-cg-pro-api-key": "",
    }
    coin_ids = "radix,bitcoin,ethereum,tether,usd-coin".split(",")

    prices = []
    for i in range(60):
        print(f"Getting prices from Gecko: {i}")
        utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
        coin_gecko_price_response = requests.get(
            url=f"https://pro-api.coingecko.com/api/v3/simple/price?ids="
            f"{','.join(coin_ids)},radix&vs_currencies=USD&include_last_updated_at=true",
            headers=headers,
        )
        coin_gecko_price = coin_gecko_price_response.json()

        for coin_id in coin_ids:
            coin_pair = f"{COIN_DICT[coin_id]}/XRD"
            prices.append(
                [
                    i,
                    "Gecko",
                    coin_pair,
                    0,
                    utc_timestamp_now - coin_gecko_price[coin_id]["last_updated_at"],
                ]
            )
        sleep(60)

    df = pd.DataFrame(prices)
    csv_file_path = "output_gecko.csv"
    df.to_csv(csv_file_path, index=False, header=False)
    print(prices)

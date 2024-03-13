import logging
from datetime import datetime, timezone
from time import sleep
import pandas as pd
import requests


if __name__ == "__main__":
    prices = []
    pairs = "BTC/XRD,ETH/XRD,USDT/XRD,USDC/XRD".split(",")
    quote_pairs = ",".join([pair.split("/")[0] for pair in pairs])
    cmc_prices = {}
    logging.info(f"Getting price for pairs: {quote_pairs}")
    url = (
        f"https://pro-api.coinmarketcap.com/v2/cryptocurrency/"
        f"quotes/latest?symbol={quote_pairs}&convert=XRD"
    )
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": f"",
    }
    for i in range(60):
        print(f"Getting prices from CMC: {i}")
        utc_timestamp_now = int(datetime.now(timezone.utc).timestamp())
        cmc_price_response = requests.get(url=url, headers=headers)
        if cmc_price_response.status_code == 200:
            logging.info(cmc_price_response.json())
            pairs_prices = cmc_price_response.json()["data"]
            for key in pairs_prices.keys():
                pair = f"{key}/XRD"

                cmc_price = pairs_prices[key][0]["quote"]["XRD"]["price"]
                last_updated_date = datetime.strptime(
                    pairs_prices[key][0]["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                last_updated_seconds = int(
                    last_updated_date.replace(tzinfo=timezone.utc).timestamp()
                )

                prices.append(
                    [
                        i,
                        "CMC",
                        pair,
                        cmc_price,
                        utc_timestamp_now - last_updated_seconds,
                    ]
                )
        sleep(60)
    df = pd.DataFrame(prices)
    csv_file_path = "output_cmc.csv"
    df.to_csv(csv_file_path, index=False, header=False)
    print(prices)

import requests
from radixdlt.config.config import Config
from radixdlt.models.oracles.token_price import OracleTokenPrice

COIN_DICT = {
    "radix": "XRD",
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "usd-coin": "USDC",
}


def calculate_xrd_quote(base_usd_price, xrd_usd_price):
    return base_usd_price / xrd_usd_price


def process_coin_gecko_prices():
    headers = {"accept": "application/json"}
    coin_ids = Config.ORACLE_COIN_GECKO_IDS.split(",")

    try:
        coin_gecko_price_response = requests.get(
            url=f"{Config.COIN_GECKO_API}/simple/price?ids="
            f"{','.join(coin_ids)},radix&vs_currencies=USD",
            headers=headers,
        )
        if coin_gecko_price_response.status_code == 200:
            coin_gecko_price = coin_gecko_price_response.json()
        else:
            raise
    except Exception:
        raise Exception("Failed to get the Coin Gecko prices")

    coin_gecko_prices = {}
    for coin_id in coin_ids:
        coin_pair = f"{COIN_DICT[coin_id]}/XRD"
        coin_gecko_xrd_price = calculate_xrd_quote(
            coin_gecko_price[coin_id]["usd"], coin_gecko_price["radix"]["usd"]
        )

        coin_gecko_prices[coin_pair] = coin_gecko_xrd_price
        OracleTokenPrice.insert_price(coin_pair, coin_gecko_xrd_price, "CoinGecko")
    return coin_gecko_prices

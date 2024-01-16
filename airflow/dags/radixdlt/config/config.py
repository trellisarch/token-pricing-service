from os import getenv


class Config:
    RADIX_CHARTS_TOKENS_PRICE_LIST = "https://api.radixapi.net/v1/token/price/list"
    RADIX_CHARTS_TOKEN_PRICE_CURRENT = "https://api.radixapi.net/v1/token/price/current"
    RADIX_CHARTS_AUTHORIZATION_TOKEN = getenv("RADIX_CHARTS_AUTHORIZATION_TOKEN")

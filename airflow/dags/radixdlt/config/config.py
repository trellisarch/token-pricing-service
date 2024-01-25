from os import getenv
from urllib.parse import quote_plus


class Config:
    RADIX_CHARTS_TOKENS_PRICE_LIST = "https://api.radixapi.net/v1/token/price/list"
    RADIX_CHARTS_TOKEN_PRICE_CURRENT = "https://api.radixapi.net/v1/token/price/current"
    RADIX_CHARTS_AUTHORIZATION_TOKEN = getenv("RADIX_CHARTS_AUTHORIZATION_TOKEN")

    POSTGRES_HOST = getenv("DB_HOST", "airflow-postgresql")
    POSTGRES_USER = getenv("DB_USER", "postgres")
    POSTGRES_PASSWORD = getenv("DB_PASSWORD", "postgres")
    ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD)
    POSTGRES_DB = getenv("DB_NAME", "dags")
    POSTGRES_PORT = getenv("DB_PORT", 5432)
    DB_URI = getenv("DB_URI", "testing")

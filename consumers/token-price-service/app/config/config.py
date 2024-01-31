import os
from urllib.parse import quote_plus


class Config:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    POSTGRES_HOST = os.environ.get("DB_HOST", "postgres")
    POSTGRES_USER = os.environ.get("DB_USER", "postgres")
    POSTGRES_PASSWORD = os.environ.get("DB_PASSWORD", "postgres@123")
    ENCODED_PASSWORD = quote_plus(POSTGRES_PASSWORD)
    POSTGRES_DB = os.environ.get("DB_NAME", "postgres")
    POSTGRES_PORT = os.environ.get("DB_PORT", 5432)
    DB_URI = f"postgresql://{POSTGRES_USER}:{ENCODED_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR")
    LOG_CONFIG_PATH = os.environ.get("LOG_CONFIG_PATH", "logging.json")
    RADIX_CHARTS_API = os.environ.get("RADIX_CHARTS_API", "https://api.radixapi.net")
    RADIX_CHARTS_MAX_TOKENS_PER_REQUEST = 30
    RADIX_CHARTS_MAX_LSUS_PER_REQUEST = 30
    SUPPORTED_CURRENCIES = "USD"
    ENTITY_DETAILS_URL = "https://mainnet.radixdlt.com/state/entity/details"
    XRD_RESOURCE_ADDRESS = (
        "resource_rdx1tknxxxxxxxxxradxrdxxxxxxxxx009923554798xxxxxxxxxradxrd"
    )

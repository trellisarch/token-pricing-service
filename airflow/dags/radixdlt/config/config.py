from os import getenv
import logging
import statsd


class SafeStats:
    def __init__(self, client):
        self._c = client
        self._logged_error = False

    def _safe(self, fn, *a, **kw):
        try:
            return fn(*a, **kw)
        except Exception:
            if not self._logged_error:
                logging.exception(
                    "StatsD client error encountered; suppressing further errors"
                )
                self._logged_error = True
            return None

    def timing(self, *a, **kw):
        return self._safe(self._c.timing, *a, **kw)

    def incr(self, *a, **kw):
        return self._safe(self._c.incr, *a, **kw)

    def gauge(self, *a, **kw):
        return self._safe(self._c.gauge, *a, **kw)


class NoOpStatsClient:
    def timing(self, *a, **kw):
        return None

    def incr(self, *a, **kw):
        return None

    def gauge(self, *a, **kw):
        return None


class Config:
    RADIX_TOKEN = "XRD"

    CAVIAR_NINE_COMPONENT_ADDRESS = (
        "component_rdx1cppy08xgra5tv5melsjtj79c0ngvrlmzl8hhs7vwtzknp9xxs63mfp"
    )

    RADIX_CHARTS_TOKENS_PRICE_LIST = "https://api.radixapi.net/v1/token/price/list"
    RADIX_CHARTS_TOKEN_PRICE_CURRENT = "https://api.radixapi.net/v1/token/price/current"
    RADIX_CHARTS_ORACLE_TOKENS = "hug,defiplaza,floop,radix"
    PYTH_ORACLE_TOKENS = ["BTC", "XRD", "ETH", "USDT", "USDC"]
    RADIX_CHARTS_AUTHORIZATION_TOKEN = getenv("RADIX_CHARTS_AUTHORIZATION_TOKEN")

    DB_URI = getenv("DB_URI")

    NETWORK_ID = int(getenv("NETWORK_ID", 1))
    NETWORK_GATEWAY = getenv("NETWORK_GATEWAY", "https://mainnet.radixdlt.com")

    COINMARKETCAP_DEV_API_KEY = getenv("COINMARKETCAP_DEV_API_KEY")
    COIN_GECKO_API = getenv("COIN_GECKO_API", "https://api.coingecko.com/api/v3")
    COIN_GECKO_API_KEY = getenv("COIN_GECKO_API_KEY", "")

    TOKEN_PRICE_SCHEDULE_INTERVAL = getenv("TOKEN_PRICE_SCHEDULE_INTERVAL", None)
    ORACLE_SCHEDULE_INTERVAL = getenv("ORACLE_SCHEDULE_INTERVAL", None)
    MARKETING_DAGS_SCHEDULE_INTERVAL = getenv("MARKETING_DAGS_SCHEDULE_INTERVAL", None)
    ORACLE_COIN_GECKO_IDS = "radix,bitcoin,ethereum,tether,usd-coin,defiplaza,hug,floop"
    ORACLE_CMC_PAIRS = "BTC/XRD,ETH/XRD,USDT/XRD,USDC/XRD"
    ORACLE_PRICE_DIFF_TRIGGER = 0.05
    ORACLE_LOCK_FEE_ADDRESS = getenv(
        "ORACLE_LOCK_FEE_ADDRESS",
        "component_tdx_2_1cptxxxxxxxxxfaucetxxxxxxxxx000527798379xxxxxxxxxyulkzl",
    )
    ORACLE_LOCK_FEE = float(getenv("ORACLE_LOCK_FEE", 0.58434484845))
    ORACLE_CONFIG_FILE = getenv("ORACLE_CONFIG_FILE", "config.json")
    STALE_PERIOD_SECS = 180

    STALE_CHECK_PAIRS = "BTC/XRD,ETH/XRD"

    TWITTER_RADIXDLT_API_KEY = getenv("TWITTER_RADIXDLT_API_KEY")
    TWITTER_RADIXDLT_API_KEY_SECRET = getenv("TWITTER_RADIXDLT_API_KEY_SECRET")
    TWITTER_RADIXDLT_ACCESS_TOKEN = getenv("TWITTER_RADIXDLT_ACCESS_TOKEN")
    TWITTER_RADIXDLT_ACCESS_TOKEN_SECRET = getenv(
        "TWITTER_RADIXDLT_ACCESS_TOKEN_SECRET"
    )
    TWITTER_RADIXDLT_BEARER_TOKEN = getenv("TWITTER_RADIXDLT_BEARER_TOKEN")

    TWITTER_SCRYPTOLANG_API_KEY = getenv("TWITTER_SCRYPTOLANG_API_KEY")
    TWITTER_SCRYPTOLANG_API_KEY_SECRET = getenv("TWITTER_SCRYPTOLANG_API_KEY_SECRET")
    TWITTER_SCRYPTOLANG_ACCESS_TOKEN = getenv("TWITTER_SCRYPTOLANG_ACCESS_TOKEN")
    TWITTER_SCRYPTOLANG_ACCESS_TOKEN_SECRET = getenv(
        "TWITTER_SCRYPTOLANG_ACCESS_TOKEN_SECRET"
    )
    TWITTER_SCRYPTOLANG_BEARER_TOKEN = getenv("TWITTER_SCRYPTOLANG_BEARER_TOKEN")

    GITHUB_TOKEN = getenv("GITHUB_TOKEN")
    TELEGRAM_RADIX_DLT_BOT_ID = getenv("TELEGRAM_RADIX_DLT_BOT_ID")
    TELEGRAM_RADIX_DLT_COMBOT_ID = getenv("TELEGRAM_RADIX_DLT_COMBOT_ID")
    TELEGRAM_RADIX_DLT_COMBOT_API_KEY = getenv("TELEGRAM_RADIX_DLT_COMBOT_API_KEY")
    TELEGRAM_RADIX_DEVS_BOT_ID = getenv("TELEGRAM_RADIX_DEVS_BOT_ID")
    TELEGRAM_RADIX_DEVS_COMBOT_ID = getenv("TELEGRAM_RADIX_DEVS_COMBOT_ID")
    TELEGRAM_RADIX_DEVS_COMBOT_API_KEY = getenv("TELEGRAM_RADIX_DEVS_COMBOT_API_KEY")

    REDDIT_CLIENT_ID = getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = getenv("REDDIT_USER_AGENT")
    REDDIT_REFRESH_TOKEN = getenv("REDDIT_REFRESH_TOKEN")

    BURNTRACKER_FIVE_BURN = (
        "https://burntracker.io/api/token/getFiveBurnData?symbol=XRD"
    )
    BURNTRACKER_BURNDATA = "https://burntracker.io/api/token/fetch_burndata_for_graph?decimal=18&symbol=XRD&type=Token&format=burn&range=24h"
    DEFILAMA_TVL = "https://api.llama.fi/v2/historicalChainTvl/Radix"
    RADIX_API_STATS = "https://api.radixapi.net/v1/network/statistics"
    COINGECKO_XRD = "https://api.coingecko.com/api/v3/coins/radix/history?date="
    COINGECKO_EXRD = "https://api.coingecko.com/api/v3/coins/e-radix/history?date="

    YOUTUBE_RADIXDLT_CHANNEL_ID = getenv("YOUTUBE_RADIXDLT_CHANNEL_ID")
    YOUTUBE_RADIXDLT_REFRESH_TOKEN = getenv("YOUTUBE_RADIXDLT_REFRESH_TOKEN")
    YOUTUBE_SCRYPTO_CHANNEL_ID = getenv("YOUTUBE_SCRYPTO_CHANNEL_ID")
    YOUTUBE_SCRYPTO_REFRESH_TOKEN = getenv("YOUTUBE_SCRYPTO_REFRESH_TOKEN")
    YOUTUBE_CLIENT_ID = getenv("YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET = getenv("YOUTUBE_CLIENT_SECRET")

    GOOGLE_RADIX_PROJECT_ID = "radix-wallet-fe520"
    GOOGLE_RADIX_STATS_BUCKET_ID = "pubsite_prod_7136842257012583290"

    NPM_PACKAGES = getenv(
        "NPM_PACKAGES",
        "@radixdlt/babylon-gateway-api-sdk,@radixdlt/radix-connect-webrtc,"
        "@radixdlt/babylon-core-api-sdk,@radixdlt/radix-engine-toolkit,"
        "@radixdlt/rola,@radixdlt/radix-dapp-toolkit",
    )
    NPM_PACKAGES_SCHEDULE_INTERVAL = getenv("NPM_PACKAGES_SCHEDULE_INTERVAL", None)

    COINGECKO_TOKEN_PRICES_SCHEDULE_INTERVAL = getenv(
        "COINGECKO_TOKEN_PRICES_SCHEDULE_INTERVAL", None
    )
    COINGECKO_TOKENS = (
        "radix,avalanche-2,e-radix,solana,polkadot,near,cardano,aptos,sui,"
        "sei-network,elrond-erd-2,the-open-network"
    )

    # Account Component Monitoring DAG
    ACC_COMP_MONITORING_SCHEDULE_INTERVAL = getenv(
        "ACC_COMP_MONITORING_SCHEDULE_INTERVAL", None
    )
    ACC_COMP_MONITORING_SLACK_WEBHOOK_URL = getenv("ACC_COMP_MONITORING_SLACK_WEBHOOK_URL")
    ACC_COMP_MONITORING_SLACK_USER_IDS = getenv("ACC_COMP_MONITORING_SLACK_USER_IDS", "")
    # JSON config: {"accounts": [{"address": "...", "name": "...", "resources": [{"address": "...", "name": "..."}]}]}
    ACC_COMP_MONITORING_CONFIG = getenv("ACC_COMP_MONITORING_CONFIG", "{}")

    STATSD_EXPORTER_INGEST_PORT = int(getenv("STATSD_EXPORTER_INGEST_PORT", "9125"))
    STATSD_HOST = getenv("STATSD_HOST", "airflow-statsd")

    try:
        _client = statsd.StatsClient(host=STATSD_HOST, port=STATSD_EXPORTER_INGEST_PORT)
    except Exception:
        logging.exception("Failed to initialize StatsD client; using NoOpStatsClient")
        _client = NoOpStatsClient()

    statsDClient = SafeStats(_client)

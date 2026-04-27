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
    DB_URI = getenv("DB_URI")

    NETWORK_ID = int(getenv("NETWORK_ID", 1))
    NETWORK_GATEWAY = getenv("NETWORK_GATEWAY", "https://mainnet.radixdlt.com")

    COIN_GECKO_API = getenv("COIN_GECKO_API", "https://api.coingecko.com/api/v3")
    COIN_GECKO_API_KEY = getenv("COIN_GECKO_API_KEY", "")

    LEDGER_PRICE_SCHEDULE_INTERVAL = getenv("LEDGER_PRICE_SCHEDULE_INTERVAL", None)

    COINGECKO_STALENESS_THRESHOLD_SECS = int(
        getenv("COINGECKO_STALENESS_THRESHOLD_SECS", "300")
    )
    COINGECKO_DIVERGENCE_THRESHOLD = float(
        getenv("COINGECKO_DIVERGENCE_THRESHOLD", "0.5")
    )
    COINGECKO_DEFAULT_WEIGHT = float(getenv("COINGECKO_DEFAULT_WEIGHT", "0.8"))

    # Account Component Monitoring DAG
    ACC_COMP_MONITORING_NETWORK_GATEWAY = getenv(
        "ACC_COMP_MONITORING_NETWORK_GATEWAY", "https://mainnet.radixdlt.com"
    )
    ACC_COMP_MONITORING_SCHEDULE_INTERVAL = getenv(
        "ACC_COMP_MONITORING_SCHEDULE_INTERVAL", None
    )
    ACC_COMP_MONITORING_SLACK_WEBHOOK_URL = getenv(
        "ACC_COMP_MONITORING_SLACK_WEBHOOK_URL"
    )
    ACC_COMP_MONITORING_SLACK_USER_IDS = getenv(
        "ACC_COMP_MONITORING_SLACK_USER_IDS", "U09AMCYQUHL,U08H9QB2FFH"
    )
    ACC_COMP_MONITORING_CONFIG = getenv(
        "ACC_COMP_MONITORING_CONFIG",
        '{"accounts": [{"address": "component_rdx1cptwph6dnf4sqv8fgs8wg03l6dv5h6hu47fr78lhs3wasanll8ukzg", "name": "component", "resources": [{"address": "resource_rdx1tk8wzyckjje4t6pz35m54ygdj4sfqkpgv8953l6w7rejhzq3nmxu9f", "name": "Rewards", "threshold": 500000}]}]}',
    )

    STATSD_EXPORTER_INGEST_PORT = int(getenv("STATSD_EXPORTER_INGEST_PORT", "9125"))
    STATSD_HOST = getenv("STATSD_HOST", "airflow-statsd")

    try:
        _client = statsd.StatsClient(host=STATSD_HOST, port=STATSD_EXPORTER_INGEST_PORT)
    except Exception:
        logging.exception("Failed to initialize StatsD client; using NoOpStatsClient")
        _client = NoOpStatsClient()

    statsDClient = SafeStats(_client)

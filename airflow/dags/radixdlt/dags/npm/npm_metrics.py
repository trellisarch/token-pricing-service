import logging
from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config
from radixdlt.models.npm.npm_model import NpmMetricsModel

logging.basicConfig(level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="npm_metrics",
    default_args=default_args,
    description="DAG to fetch npm metrics",
    schedule_interval=Config.TOKEN_PRICE_SCHEDULE_INTERVAL,
    catchup=False,
)
def npm_metrics():
    @task
    def fetch_npm_metrics(package):
        NpmMetricsModel.fetch_and_save_data(package)

    for package in Config.NPM_PACKAGES.split(","):
        fetch_npm_metrics(package)


npm_metrics()

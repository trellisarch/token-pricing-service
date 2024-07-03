import logging
from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config
from radixdlt.models.crates_io.crates_model import CratesData

logging.basicConfig(level=logging.INFO)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    dag_id="crates_io_metrics",
    default_args=default_args,
    description="DAG to fetch crates.io metrics",
    schedule_interval=Config.MARKETING_DAGS_SCHEDULE_INTERVAL,
    catchup=False,
)
def crates_io_metrics():
    @task
    def fetch_downloads_metrics(crate):
        CratesData.fetch_and_save_data(crate)

    fetch_downloads_metrics("radix-engine")
    fetch_downloads_metrics("radix-rust")
    fetch_downloads_metrics("sbor-derive-common")
    fetch_downloads_metrics("sbor-derive")
    fetch_downloads_metrics("sbor")
    fetch_downloads_metrics("radix-sbor-derive")
    fetch_downloads_metrics("radix-common")
    fetch_downloads_metrics("radix-common-derive")
    fetch_downloads_metrics("radix-blueprint-schema-init")
    fetch_downloads_metrics("radix-engine-interface")
    fetch_downloads_metrics("scrypto-derive")
    fetch_downloads_metrics("scrypto")
    fetch_downloads_metrics("radix-substate-store-interface")
    fetch_downloads_metrics("radix-substate-store-impls")
    fetch_downloads_metrics("radix-engine-profiling")
    fetch_downloads_metrics("radix-engine-profiling-derive")
    fetch_downloads_metrics("radix-native-sdk")
    fetch_downloads_metrics("radix-transactions")
    fetch_downloads_metrics("radix-engine")
    fetch_downloads_metrics("radix-transaction-scenarios")
    fetch_downloads_metrics("radix-substate-store-queries")
    fetch_downloads_metrics("scrypto-bindgen")
    fetch_downloads_metrics("scrypto-compiler")
    fetch_downloads_metrics("scrypto-test")
    fetch_downloads_metrics("radix-clis")


crates_io_metrics()

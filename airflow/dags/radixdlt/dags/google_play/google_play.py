import json
import logging
from io import BytesIO
from os import getenv
from os.path import join, dirname, abspath

import pandas as pd
from datetime import datetime, timedelta
from google.cloud import storage
from pandas import DataFrame

from radixdlt.config.config import Config
from airflow.decorators import task, dag

from radixdlt.models.google_play.stats_install import GooglePlayInstalls
from radixdlt.models.google_play.stats_ratings import GooglePlayRatings
from radixdlt.models.google_play.stats_store_performance import (
    GooglePlayStorePerformance,
)

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}


logging.basicConfig(level=logging.INFO)


@dag(
    schedule_interval=Config.MARKETING_DAGS_SCHEDULE_INTERVAL,
    default_args=default_args,
    catchup=False,
    dag_id="google_play",
)
def google_play_stats():
    @task
    def get_service_account():
        service_account = getenv("GOOGLE_SERVICE_ACCOUNT")
        service_account_file = getenv("GOOGLE_APPLICATION_CREDENTIALS")
        with open(service_account_file, "w") as file:
            file.write(service_account)
        return True

    @task
    def get_install_stats(service_account: bool):
        if service_account:
            client = storage.Client(project=Config.GOOGLE_RADIX_PROJECT_ID)
            blobs = client.list_blobs(
                Config.GOOGLE_RADIX_STATS_BUCKET_ID, prefix="stats/installs"
            )
            csv_blobs = [
                blob for blob in blobs if blob.name.endswith("app_version.csv")
            ]
            csv_blobs.sort(key=lambda blob: blob.time_created, reverse=True)
            latest_blob = csv_blobs[0]
            content = latest_blob.download_as_string().decode("utf-16")
            file_object = BytesIO(content.encode())
            return pd.read_csv(
                filepath_or_buffer=file_object, delimiter=",", skipinitialspace=True
            )

    @task
    def save_install_stats(stats_data_frame: DataFrame):
        GooglePlayInstalls.insert_csv_data(stats_data_frame)

    @task
    def get_ratings_stats(service_account: bool):
        if service_account:
            client = storage.Client(project=Config.GOOGLE_RADIX_PROJECT_ID)
            blobs = client.list_blobs(
                Config.GOOGLE_RADIX_STATS_BUCKET_ID, prefix="stats/ratings"
            )
            csv_blobs = [
                blob for blob in blobs if blob.name.endswith("app_version.csv")
            ]
            csv_blobs.sort(key=lambda blob: blob.time_created, reverse=True)
            latest_blob = csv_blobs[0]
            content = latest_blob.download_as_string().decode("utf-16")
            file_object = BytesIO(content.encode())
            return pd.read_csv(
                filepath_or_buffer=file_object, delimiter=",", skipinitialspace=True
            )

    @task
    def save_ratings_stats(stats_data_frame: DataFrame):
        GooglePlayRatings.insert_csv_data(stats_data_frame)

    @task
    def get_store_performance_stats(service_account: bool):
        if service_account:
            client = storage.Client(project=Config.GOOGLE_RADIX_PROJECT_ID)
            blobs = client.list_blobs(
                Config.GOOGLE_RADIX_STATS_BUCKET_ID, prefix="stats/store_performance"
            )
            csv_blobs = [blob for blob in blobs if blob.name.endswith("country.csv")]
            csv_blobs.sort(key=lambda blob: blob.time_created, reverse=True)
            latest_blob = csv_blobs[0]
            content = latest_blob.download_as_string().decode("utf-16")
            file_object = BytesIO(content.encode())
            return pd.read_csv(
                filepath_or_buffer=file_object, delimiter=",", skipinitialspace=True
            )

    @task
    def save_store_performance_stats(stats_data_frame: DataFrame):
        GooglePlayStorePerformance.insert_csv_data(stats_data_frame)

    save_install_stats(get_install_stats(get_service_account()))
    save_ratings_stats(get_ratings_stats(get_service_account()))
    save_store_performance_stats(get_store_performance_stats(get_service_account()))


google_play_stats()

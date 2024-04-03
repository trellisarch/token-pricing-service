import logging
from os.path import join, dirname, abspath

import pandas as pd
from datetime import datetime, timedelta
from google.cloud import storage
from pandas import DataFrame

from radixdlt.config.config import Config
from airflow.decorators import task, dag

from radixdlt.models.goodle_play.stats_install import GooglePlayInstalls
from radixdlt.models.goodle_play.stats_ratings import GooglePlayRatings

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
    def get_install_stats():

        # client = storage.Client(project=Config.GOOGLE_RADIX_PROJECT_ID)
        # blobs = client.list_blobs(Config.GOOGLE_RADIX_STATS_BUCKET_ID, prefix="stats/installs")
        # csv_blobs = [blob for blob in blobs if blob.name.endswith(".csv")]
        # csv_blobs.sort(key=lambda blob: blob.creation_time, reverse=True)
        # return pd.read_csv(csv_blobs[0], encoding="utf-8")

        csv_file_path = join(
            dirname(dirname(abspath(__file__))),
            "google_play",
            "stats_installs.csv",
        )

        return pd.read_csv(
            filepath_or_buffer=csv_file_path,
            delimiter=",",
            skipinitialspace=True,
            encoding="utf-16",
        )

    @task
    def save_install_stats(stats_data_frame: DataFrame):
        GooglePlayInstalls.insert_csv_data(stats_data_frame)

    @task
    def get_ratings_stats():
        # client = storage.Client(project=Config.GOOGLE_RADIX_PROJECT_ID)
        # blobs = client.list_blobs(Config.GOOGLE_RADIX_STATS_BUCKET_ID, prefix="stats/installs")
        # csv_blobs = [blob for blob in blobs if blob.name.endswith(".csv")]
        # csv_blobs.sort(key=lambda blob: blob.creation_time, reverse=True)
        # return pd.read_csv(csv_blobs[0], encoding="utf-8")

        csv_file_path = join(
            dirname(dirname(abspath(__file__))),
            "google_play",
            "stats_ratings.csv",
        )

        return pd.read_csv(
            filepath_or_buffer=csv_file_path,
            delimiter=",",
            skipinitialspace=True,
            encoding="utf-16",
        )

    @task
    def save_ratings_stats(stats_data_frame: DataFrame):
        GooglePlayRatings.insert_csv_data(stats_data_frame)

    save_install_stats(get_install_stats())
    save_ratings_stats(get_ratings_stats())


google_play_stats()

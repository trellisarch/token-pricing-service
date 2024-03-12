import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from radixdlt.config.config import Config
from radixdlt.models.youtube.youtube_model import YoutubeData
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "youtube",
    default_args=default_args,
    schedule_interval=Config.DAGS_SCHEDULE_INTERVAL,
    catchup=False,
)

logging.basicConfig(level=logging.INFO)


def get_youtube_info(user_name, channel, refresh_token):
    try:
        client_id = Config.YOUTUBE_CLIENT_ID
        client_secret = Config.YOUTUBE_CLIENT_SECRET

        credentials = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/yt-analytics.readonly"],
        )
        credentials.refresh(Request())

        YoutubeData.fetch_and_save_data(user_name, channel, credentials)

    except Exception as e:
        logging.error("Error occurred while fetching youtube information: %s", e)
        raise


# Define the PythonOperator with a function that takes the repository name as a parameter
def repo_task(user_name, channel, refresh_token):
    return PythonOperator(
        task_id=f"fetch_youtube_user_{user_name}",
        python_callable=lambda: get_youtube_info(user_name, channel, refresh_token),
        dag=dag,
    )


youtube_user_task1 = repo_task(
    "RadixDLT",
    Config.YOUTUBE_RADIXDLT_CHANNEL_ID,
    Config.YOUTUBE_RADIXDLT_REFRESH_TOKEN,
)

youtube_user_task2 = repo_task(
    "scrypto_radix",
    Config.YOUTUBE_SCRYPTO_CHANNEL_ID,
    Config.YOUTUBE_SCRYPTO_REFRESH_TOKEN,
)

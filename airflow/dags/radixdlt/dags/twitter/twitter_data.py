import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import tweepy
from radixdlt.config.config import Config
from radixdlt.models.twitter.twitter_model import TwitterData

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "twitter",
    default_args=default_args,
    schedule_interval=Config.ORACLE_SCHEDULE_INTERVAL,
)


def get_twitter_followers(
    user_name, consumer_key, consumer_secret, access_token, access_token_secret
):
    try:
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )

        api = tweepy.API(auth, wait_on_rate_limit=True)

        # Retrieve user credentials
        user_info = api.verify_credentials()

        TwitterData.fetch_and_save_data(user_name, user_info)

    except Exception as e:
        logging.error("Error occurred while fetching Twitter followers: %s", e)


# Define the PythonOperator with a function that takes the repository name as a parameter
def repo_task(
    user_name, consumer_key, consumer_secret, access_token, access_token_secret
):
    return PythonOperator(
        task_id=f"fetch_twitter_user_{user_name}",
        python_callable=lambda: get_twitter_followers(
            user_name, consumer_key, consumer_secret, access_token, access_token_secret
        ),
        dag=dag,
    )


twitter_user_task1 = repo_task(
    "radixdlt",
    Config.TWITTER_RADIXDLT_API_KEY,
    Config.TWITTER_RADIXDLT_API_KEY_SECRET,
    Config.TWITTER_RADIXDLT_ACCESS_TOKEN,
    Config.TWITTER_RADIXDLT_ACCESS_TOKEN_SECRET,
)

twitter_user_task2 = repo_task(
    "scrypto_lang",
    Config.TWITTER_SCRYPTOLANG_API_KEY,
    Config.TWITTER_SCRYPTOLANG_API_KEY_SECRET,
    Config.TWITTER_SCRYPTOLANG_ACCESS_TOKEN,
    Config.TWITTER_SCRYPTOLANG_ACCESS_TOKEN_SECRET,
)


# Set dependencies
twitter_user_task1

twitter_user_task2

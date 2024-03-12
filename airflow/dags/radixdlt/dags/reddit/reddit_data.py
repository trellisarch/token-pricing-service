import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import praw
from radixdlt.config.config import Config
from radixdlt.models.reddit.reddit_redditor_model import RedditRedditorData
from radixdlt.models.reddit.reddit_subreddit_model import RedditSubredditData


# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "reddit",
    default_args=default_args,
    schedule_interval=Config.ORACLE_SCHEDULE_INTERVAL,
    catchup=False,
)

client_id = Config.REDDIT_CLIENT_ID
client_secret = Config.REDDIT_CLIENT_SECRET
user_agent = Config.REDDIT_USER_AGENT
refresh_token = Config.REDDIT_REFRESH_TOKEN


def get_reddit_redditor_data(user_name):
    try:
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        redditor = reddit.redditor(user_name)

        RedditRedditorData.fetch_and_save_data(user_name, redditor)

    except Exception as e:
        logging.error("Error occurred while fetching Redditor data: %s", e)
        raise


def get_reddit_subreddit_data(user_name):
    try:
        # Initialize Reddit instance
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            refresh_token=refresh_token,
        )

        subreddit = reddit.subreddit(user_name)

        RedditSubredditData.fetch_and_save_data(user_name, subreddit)

    except Exception as e:
        logging.error("Error occurred while fetching Subredditor data: %s", e)
        raise


# Define the PythonOperator with a function that takes the repository name as a parameter
def redditor_task(user_name):
    return PythonOperator(
        task_id=f"fetch_reddit_redditor_{user_name}",
        python_callable=lambda: get_reddit_redditor_data(user_name),
        dag=dag,
    )


# Define the PythonOperator with a function that takes the repository name as a parameter
def subreddit_task(user_name):
    return PythonOperator(
        task_id=f"fetch_reddit_subreddit_{user_name}",
        python_callable=lambda: get_reddit_subreddit_data(user_name),
        dag=dag,
    )


reddit_redditor_task1 = redditor_task("Radix_DLT")

reddit_subreddit_task1 = subreddit_task("Radix")

reddit_subreddit_task2 = subreddit_task("RadixValidators")

reddit_subreddit_task3 = subreddit_task("RadixDevelopers")

reddit_subreddit_task4 = subreddit_task("radix_dlt")

reddit_subreddit_task5 = subreddit_task("scrypto")


# Set dependencies

reddit_redditor_task1 >> reddit_subreddit_task1
reddit_redditor_task1 >> reddit_subreddit_task2
reddit_redditor_task1 >> reddit_subreddit_task3
reddit_redditor_task1 >> reddit_subreddit_task4
reddit_redditor_task1 >> reddit_subreddit_task5

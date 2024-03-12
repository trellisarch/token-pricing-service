import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
from radixdlt.config.config import Config
from radixdlt.models.telegram.telegram_model import TelegramData


# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "telegram",
    default_args=default_args,
    schedule_interval=Config.ORACLE_SCHEDULE_INTERVAL,
    catchup=False,
)

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_telegram_info(user_name, bot_id, combot_id, combot_api_key):
    try:
        # Your Telegram API logic to fetch the user count
        headers = {"accept": "application/json"}

        bot_response = requests.post(
            f"https://api.telegram.org/{bot_id}/getChatMemberCount?chat_id=@{user_name}",
            headers=headers,
        )

        bot_response.raise_for_status()  # Raise an HTTPError for bad responses

        current_time = datetime.now()  # Use UTC time instead of local time

        # Calculate timestamps
        from_timestamp = int(
            (current_time - timedelta(days=1))
            .replace(hour=0, minute=0, second=0)
            .timestamp()
        )

        to_timestamp = int(
            (
                current_time.replace(hour=23, minute=59, second=59)
                + timedelta(seconds=1)
            ).timestamp()
        )

        # Your combot API URL
        combot_api_url = f"https://api.combot.org/v2/a/g/?chat_id=-{combot_id}&from={from_timestamp}&to={to_timestamp}&api_key={combot_api_key}"

        # Use this URL in your requests.get()
        combot_response = requests.get(combot_api_url)

        TelegramData.fetch_and_save_data(
            user_name, bot_response.json()["result"], combot_response.json()[0]
        )

    except Exception as e:
        logging.error("Error occurred while fetching Telegram information: %s", e)
        raise


# Define the PythonOperator with a function that takes the repository name as a parameter
def repo_task(user_name, bot_id, combot_id, combot_api_key):
    return PythonOperator(
        task_id=f"fetch_telegram_user_{user_name}",
        python_callable=lambda: get_telegram_info(
            user_name, bot_id, combot_id, combot_api_key
        ),
        dag=dag,
    )


telegram_user_task1 = repo_task(
    "radix_dlt",
    Config.TELEGRAM_RADIX_DLT_BOT_ID,
    Config.TELEGRAM_RADIX_DLT_COMBOT_ID,
    Config.TELEGRAM_RADIX_DLT_COMBOT_API_KEY,
)
telegram_user_task2 = repo_task(
    "RadixDevelopers",
    Config.TELEGRAM_RADIX_DEVS_BOT_ID,
    Config.TELEGRAM_RADIX_DEVS_COMBOT_ID,
    Config.TELEGRAM_RADIX_DEVS_COMBOT_API_KEY,
)

telegram_user_task1

telegram_user_task2

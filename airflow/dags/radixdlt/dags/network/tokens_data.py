import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from radixdlt.config.config import Config
from radixdlt.models.network.tokens_model import TokensData
import requests

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 6),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "tokens",
    default_args=default_args,
    schedule_interval=Config.MARKETING_DAGS_SCHEDULE_INTERVAL,
    catchup=False,
)


def get_tokens(token_id):
    conn = None
    cursor = None

    headers = {
        "accept": "application/json",
        "x-cg-pro-api-key": Config.COIN_GECKO_API_KEY,
    }

    try:
        coin_gecko_price_response = requests.get(
            url=f"{Config.COIN_GECKO_API}/coins/{token_id}",
            headers=headers,
        )

        TokensData.fetch_and_save_data(token_id, coin_gecko_price_response)

    except Exception as e:
        logging.error("Error occurred while fetching info: %s", e)
        raise


def repo_task(coin_name):
    return PythonOperator(
        task_id=f"get_tokens_task_{coin_name.replace('-', '_')}",
        python_callable=lambda: get_tokens(coin_name),
        dag=dag,
    )


radix_task = repo_task("radix")

eradix_task = repo_task("e-radix")

avalanche2_task = repo_task("avalanche-2")

solana_task = repo_task("solana")

polkadot_task = repo_task("polkadot")

near_task = repo_task("near")

near_task = repo_task("sui")

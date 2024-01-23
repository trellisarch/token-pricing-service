import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from radixdlt.config.config import Config
from radixdlt.lib.http import get_radix_charts_headers
from radixdlt.models.radix_charts.token import Token

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "radix_charts_tokens_list",
    default_args=default_args,
    description="DAG to insert tokens into PostgreSQL",
    schedule_interval="@daily",
)


def fetch_tokens():
    api_endpoint = Config.RADIX_CHARTS_TOKENS_PRICE_LIST
    logging.info(get_radix_charts_headers())
    response = requests.get(api_endpoint, headers=get_radix_charts_headers())
    logging.info(response.text)
    tokens = response.json()["data"]
    logging.info(tokens)
    return tokens


def insert_tokens(**kwargs):
    tokens = kwargs["ti"].xcom_pull(task_ids="fetch_tokens")
    Token.insert_tokens(tokens)


fetch_tokens_task = PythonOperator(
    task_id="fetch_tokens",
    python_callable=fetch_tokens,
    dag=dag,
)

insert_tokens_task = PythonOperator(
    task_id="insert_tokens",
    python_callable=insert_tokens,
    provide_context=True,
    dag=dag,
)

fetch_tokens_task >> insert_tokens_task

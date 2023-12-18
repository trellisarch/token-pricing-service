from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

from radixdlt.config.config import Config
from radixdlt.lib.http import get_headers
from radixdlt.lib.psql import get_postgres_connection

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 18),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('radix_charts_tokens_list',
          default_args=default_args,
          description='DAG to insert tokens into PostgreSQL',
          schedule_interval='@daily'
          )


def fetch_tokens():
    # Fetch tokens from API
    api_endpoint = Config.RADIX_CHARTS_TOKENS_PRICE_LIST
    response = requests.get(api_endpoint, get_headers())
    tokens = response.json()['data']

    return tokens


def insert_tokens(**kwargs):
    tokens = kwargs['ti'].xcom_pull(task_ids='fetch_tokens')

    # Connect to PostgreSQL
    conn = get_postgres_connection()
    cursor = conn.cursor()

    # Insert tokens into the PostgreSQL table if they don't already exist
    for token in tokens:
        cursor.execute("SELECT * FROM tokens WHERE token = %s", (token,))
        existing_token = cursor.fetchone()
        if not existing_token:
            cursor.execute("INSERT INTO tokens (token) VALUES (%s)", (token,))

    conn.commit()
    cursor.close()
    conn.close()


fetch_tokens_task = PythonOperator(
    task_id='fetch_tokens',
    python_callable=fetch_tokens,
    dag=dag,
)

insert_tokens_task = PythonOperator(
    task_id='insert_tokens',
    python_callable=insert_tokens,
    provide_context=True,
    dag=dag,
)

fetch_tokens_task >> insert_tokens_task

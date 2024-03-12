from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from radixdlt.models.radix_charts.token import RadixToken
from radixdlt.models.radix_charts.token_price import RadixTokenPrice

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "radix_charts_current_price",
    default_args=default_args,
    description="DAG to fetch tokens price and save to PostgreSQL",
    schedule_interval=None,
)


def fetch_tokens_and_save_price(**kwargs):
    tokens = RadixToken.list_tokens()
    RadixTokenPrice.fetch_and_save_prices(tokens)


fetch_tokens_price_task = PythonOperator(
    task_id="fetch_tokens_price",
    python_callable=fetch_tokens_and_save_price,
    provide_context=True,
    dag=dag,
)

fetch_tokens_price_task

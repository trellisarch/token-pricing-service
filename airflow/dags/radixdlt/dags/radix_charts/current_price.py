from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from radixdlt.lib.psql import get_postgres_connection
from radixdlt.models.radix_charts.token_price import TokenPrice

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 14),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "radix_charts_current_price",
    default_args=default_args,
    description="DAG to fetch tokens price and save to PostgreSQL",
    schedule_interval="* * * * *",
)


def fetch_tokens_and_save_price(**kwargs):
    conn = get_postgres_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT resource_address FROM token")
    tokens = cursor.fetchall()

    TokenPrice.fetch_and_save_prices(tokens)

    conn.commit()
    cursor.close()
    conn.close()


fetch_tokens_price_task = PythonOperator(
    task_id="fetch_tokens_price",
    python_callable=fetch_tokens_and_save_price,
    provide_context=True,
    dag=dag,
)

fetch_tokens_price_task

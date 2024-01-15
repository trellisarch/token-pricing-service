import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from radixdlt.config.config import Config
from radixdlt.lib.http import get_radix_charts_headers
from radixdlt.lib.psql import get_postgres_connection

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

    current_price_endpoint = Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT
    chunked_tokens = [tokens[i : i + 30] for i in range(0, len(tokens), 30)]

    for chunk in chunked_tokens:
        addresses = ",".join(token[0] for token in chunk)

        params = {"resource_addresses": addresses}
        response = requests.get(url=current_price_endpoint,
                                params=params,
                                headers=get_radix_charts_headers())
        price_data = response.json()["data"]
        logging.info(price_data)

        for resource_address in price_data.keys():
            cursor.execute(
                "INSERT INTO token_prices (resource_address, usd_price,"
                "usd_market_cap, usd_vol_24h, last_updated_at)"
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    resource_address,
                    price_data[resource_address]["usd_price"],
                    price_data[resource_address]["usd_market_cap"],
                    price_data[resource_address]["usd_vol_24h"],
                    datetime.fromtimestamp(
                        price_data[resource_address]["last_updated_at"]
                    ),
                ),
            )

    conn.commit()
    cursor.close()
    conn.close()


fetch_tokens_price_task = PythonOperator(
    task_id="fetch_tokens_price",
    python_callable=fetch_tokens_and_save_price,
    provide_context=True,
    dag=dag,
)

fetch_tokens_and_save_price

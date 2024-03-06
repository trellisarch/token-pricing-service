import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from radixdlt.config.config import Config
from radixdlt.models.network.network_model import NetworkData
from radixdlt.lib.http import get_radix_charts_headers
import requests

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 4),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG("network", default_args=default_args, schedule_interval="0 0 * * *")


def get_network():
    conn = None
    cursor = None

    try:

        # Make a GET request to the API
        response_five = requests.get(Config.BURNTRACKER_FIVE_BURN)
        response_burn = requests.get(Config.BURNTRACKER_BURNDATA)
        response_defillama = requests.get(Config.DEFILAMA_TVL)
        response_radixapi = requests.get(
            Config.RADIX_API_STATS, headers=get_radix_charts_headers()
        )

        NetworkData.fetch_and_save_data(
            response_five,
            response_burn,
            response_defillama,
            response_radixapi,
        )

    except Exception as e:
        logging.error("Error occurred while fetching repository info: %s", e)


# Define the PythonOperator with a function that takes the repository name as a parameter
def network_task():
    return PythonOperator(
        task_id="get_network_task",
        python_callable=lambda: get_network(),
        dag=dag,
    )


# Set dependencies
network_task()

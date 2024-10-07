import logging
from airflow.decorators import task, dag
from datetime import datetime, timedelta
from radixdlt.config.config import Config


# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="watchdog",
    default_args=default_args,
    description="DAG to check proper behaviour of Scheduler ",
    schedule_interval="* * * * *",
    catchup=False,
)
def watchdog_task():
    @task
    def watchdog_counter():
        logging.info("Watchdog counter increased")
        Config.statsDClient.incr(f"dag_watchdog.custom_counter.passed")

    watchdog_counter()


watchdog_task()

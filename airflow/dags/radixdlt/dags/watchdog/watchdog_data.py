import logging
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "watchdog",
    default_args=default_args,
    schedule_interval="* * * * *",
    catchup=False,
)

logging.basicConfig(level=logging.INFO)


# Define a task (Dummy task for now)
start = DummyOperator(
    task_id="start_task",
    dag=dag,
)

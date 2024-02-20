import sys
from datetime import datetime, timedelta
from airflow.decorators import task, dag

import missing_library

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 22),
    "retries": 1,
    "retry_delay": timedelta(seconds=5),
}


@dag(
    schedule=None, default_args=default_args, catchup=False, dag_id="test_import_error"
)
def test():

    @task
    def test_task():
        sys.exit(1)

    test_task()


test()

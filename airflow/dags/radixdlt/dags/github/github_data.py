import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from github import Github
from radixdlt.config.config import Config
from radixdlt.models.github.github_accounts_model import (
    GithubAccountsData,
)
from radixdlt.models.github.github_repositories_model import (
    GithubRepositoriesData,
)
from statsd import StatsClient  # Import StatsClient

# StatsD Configuration
STATSD_HOST = 'localhost'
STATSD_PORT = 8125

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 5),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "github",
    default_args=default_args,
    schedule_interval=Config.DAGS_SCHEDULE_INTERVAL,
    catchup=False,
)


def get_github_user(user_name):
    try:
        # Set up your GitHub API credentials
        github_token = Config.GITHUB_TOKEN
        github_client = Github(github_token)

        user_response = github_client.get_user(user_name)

        GithubAccountsData.fetch_and_save_data(user_name, user_response)

    except Exception as e:
        logging.error("Error occurred while fetching Github information: %s", e)
        raise


def get_github_repo(user_name, repo_name):
    conn = None
    cursor = None

    try:
        # Set up your GitHub API credentials
        github_token = Config.GITHUB_TOKEN
        github_client = Github(github_token)

        repo_response = github_client.get_repo(user_name + "/" + repo_name)

        GithubRepositoriesData.fetch_and_save_data(user_name, repo_name, repo_response)

    except Exception as e:
        logging.error("Error occurred while fetching repository info: %s", e)
        raise


# Define the PythonOperator with a function that takes the repository name as a parameter
def repo_task(user_name, repo_name):
    return PythonOperator(
        task_id=f"get_github_repo_task_{repo_name.replace('/', '_')}",
        python_callable=lambda: get_github_repo(user_name, repo_name),
        dag=dag,
    )


# Define the PythonOperators
github_user_task = PythonOperator(
    task_id=f"get_github_user_task_radixdlt",
    python_callable=lambda: get_github_user("radixdlt"),
    dag=dag,
)

github_repo_task1 = repo_task("radixdlt", "radixdlt-scrypto")
github_repo_task2 = repo_task("radixdlt", "radix-engine-toolkit")
github_repo_task3 = repo_task("radixdlt", "babylon-nginx")
github_repo_task4 = repo_task("radixdlt", "babylon-nodecli")
github_repo_task5 = repo_task("radixdlt", "radix-helm-charts")
github_repo_task6 = repo_task("radixdlt", "babylon-gateway")
github_repo_task7 = repo_task("radixdlt", "babylon-node")
github_repo_task8 = repo_task("radixdlt", "typescript-radix-engine-toolkit")
github_repo_task10 = repo_task("radixdlt", "connect-button")
github_repo_task11 = repo_task("radixdlt", "radix-dapp-toolkit")
github_repo_task12 = repo_task("radixdlt", "wallet-sdk")
github_repo_task13 = repo_task("radixdlt", "rola")
github_repo_task14 = repo_task("radixdlt", "create-radix-dapp")
github_repo_task15 = repo_task("radixdlt", "radix-engine-toolkit-examples")
github_repo_task16 = repo_task("radixdlt", "official-examples")
github_repo_task17 = repo_task("radixdlt", "experimental-examples")

# Set dependencies
github_user_task >> github_repo_task1
github_user_task >> github_repo_task2
github_user_task >> github_repo_task3
github_user_task >> github_repo_task4
github_user_task >> github_repo_task5
github_user_task >> github_repo_task6
github_user_task >> github_repo_task7
github_user_task >> github_repo_task8
github_user_task >> github_repo_task10
github_user_task >> github_repo_task11
github_user_task >> github_repo_task12
github_user_task >> github_repo_task13
github_user_task >> github_repo_task14
github_user_task >> github_repo_task15
github_user_task >> github_repo_task16
github_user_task >> github_repo_task17

# Function to get the status of the current DAG run
def get_current_dag_run_status():
    dag_runs = dag.get_dagruns(start_date=datetime.now(), end_date=datetime.now())
    last_dag_run = next(iter(dag_runs), None)  # Get the latest dag run

    if last_dag_run:
        return last_dag_run.state if last_dag_run.state in ['success', 'failed'] else 'running'
    return 'unknown'

# Export metric using StatsD
def export_statsd_metric():
    last_run_status = get_current_dag_run_status()
    statsd_client = StatsClient(STATSD_HOST, STATSD_PORT)
    statsd_client.gauge('last_run_status', last_run_status)


# Define the task to export the metric
export_metric_task = PythonOperator(
    task_id='export_metric_task',
    python_callable=export_statsd_metric,  # Use export_statsd_metric here
    dag=dag,
)

# Set dependencies to be run after dag succeed or fail
github_user_task >> export_metric_task
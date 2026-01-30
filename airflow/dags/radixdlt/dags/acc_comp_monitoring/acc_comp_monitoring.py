import json
import logging
from datetime import datetime, timedelta

import requests
from airflow.decorators import task, dag

from radixdlt.config.config import Config
from radixdlt.models.acc_comp_monitoring.balance_history_model import BalanceHistory

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


def get_account_details(account_address: str) -> dict:
    """Call the Radix Gateway state/entity/details endpoint."""
    url = f"{Config.ACC_COMP_MONITORING_NETWORK_GATEWAY}/state/entity/details"
    response = requests.post(
        url,
        json={"addresses": [account_address]},
        headers={"accept": "application/json", "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_balance(resource_address: str, account_address: str) -> float:
    """Get the balance of a specific resource for an account."""
    account_details = get_account_details(account_address)
    account_items = account_details["items"][0]
    fungible_resources = account_items.get("fungible_resources", {}).get("items", [])

    for item in fungible_resources:
        if item.get("resource_address") == resource_address:
            return float(item.get("amount", 0))

    return 0.0


@dag(
    dag_id="acc_comp_monitoring",
    default_args=default_args,
    description="DAG to monitor account components via Radix Gateway and notify via Slack",
    schedule_interval=Config.ACC_COMP_MONITORING_SCHEDULE_INTERVAL,
    catchup=False,
)
def acc_comp_monitoring_dag():
    @task
    def check_balances():
        """Check balances for all configured accounts and resources."""
        config_str = Config.ACC_COMP_MONITORING_CONFIG
        if not config_str or config_str == "{}":
            raise ValueError("ACC_COMP_MONITORING_CONFIG is not configured")

        config = json.loads(config_str)
        accounts = config.get("accounts", [])

        if not accounts:
            raise ValueError("No accounts configured in ACC_COMP_MONITORING_CONFIG")

        changes = []

        for account in accounts:
            account_address = account.get("address")
            account_name = account.get("name", account_address[:20] + "...")
            resources = account.get("resources", [])

            logging.info(f"Checking account: {account_name}")

            for resource in resources:
                resource_address = resource.get("address")
                resource_name = resource.get("name", resource_address[:20] + "...")
                threshold = resource.get("threshold", 0)

                # Get current balance from Gateway
                current_balance = get_balance(resource_address, account_address)

                # Get previous balance from database
                previous_balance = BalanceHistory.get_previous_balance(
                    account_address, resource_address
                )

                # Save current balance to database
                BalanceHistory.save_balance(
                    account_address=account_address,
                    resource_address=resource_address,
                    resource_name=resource_name,
                    balance=current_balance,
                    previous_balance=previous_balance,
                )

                # Check for changes exceeding threshold
                if previous_balance is not None:
                    change = current_balance - previous_balance
                    if abs(change) > threshold:
                        changes.append(
                            {
                                "account_name": account_name,
                                "account_address": account_address,
                                "resource_name": resource_name,
                                "resource_address": resource_address,
                                "previous_balance": previous_balance,
                                "current_balance": current_balance,
                                "change": change,
                                "threshold": threshold,
                            }
                        )
                        logging.info(
                            f"Balance change exceeds threshold: {account_name} {resource_name} "
                            f"{previous_balance} -> {current_balance} (change: {change}, threshold: {threshold})"
                        )
                    else:
                        logging.info(
                            f"Balance change within threshold: {account_name} {resource_name} "
                            f"change: {change}, threshold: {threshold}"
                        )

        return changes

    @task
    def send_slack_notification(changes: list):
        """Send Slack notification if there are balance changes."""
        webhook_url = Config.ACC_COMP_MONITORING_SLACK_WEBHOOK_URL
        if not webhook_url:
            logging.warning(
                "ACC_COMP_MONITORING_SLACK_WEBHOOK_URL not configured, skipping notification"
            )
            return

        if not changes:
            logging.info("No balance changes detected, skipping notification")
            return

        # Format user mentions
        user_ids = [
            uid.strip()
            for uid in Config.ACC_COMP_MONITORING_SLACK_USER_IDS.split(",")
            if uid.strip()
        ]
        mentions = " ".join(f"<@{uid}>" for uid in user_ids)

        # Build message
        change_lines = []
        for c in changes:
            sign = "+" if c["change"] > 0 else ""
            change_lines.append(
                f"• *{c['account_name']}* - {c['resource_name']}: "
                f"{c['previous_balance']:,.2f} → {c['current_balance']:,.2f} "
                f"({sign}{c['change']:,.2f}, threshold: {c['threshold']:,.2f})"
            )

        message = {
            "text": (
                f"{mentions} *Account Component Monitoring - Balance Changes Detected*\n\n"
                + "\n".join(change_lines)
            )
        }

        response = requests.post(
            webhook_url,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        logging.info(f"Slack notification sent for {len(changes)} balance changes")

    changes = check_balances()
    send_slack_notification(changes)


acc_comp_monitoring_dag()

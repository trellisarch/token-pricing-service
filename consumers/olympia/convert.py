import argparse
import logging
import os
from os.path import dirname, abspath, join
from datetime import datetime
from radix_engine_toolkit import (
    OlympiaAddress,
    derive_virtual_account_address_from_olympia_account_address,
    derive_resource_address_from_olympia_resource_address,
)
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def derive_babylon_account_address(address):
    olympia_address = OlympiaAddress(address)
    babylon_address = derive_virtual_account_address_from_olympia_account_address(
        network_id=1, olympia_account_address=olympia_address
    )
    return babylon_address.as_str()


def derive_babylon_resource_address(address):
    olympia_resource_address = OlympiaAddress(address)
    return derive_resource_address_from_olympia_resource_address(
        network_id=1, olympia_resource_address=olympia_resource_address
    ).as_str()


def convert_account_address():
    csv_file_path = "resources/olympia_accounts_addresses.csv"
    df = pd.read_csv(csv_file_path)
    df["babylon_address"] = df["olympia_address"].apply(
        lambda x: derive_babylon_account_address(x)
    )

    df = df[
        [
            "olympia_gateway_id",
            "olympia_address",
            "babylon_address",
            "initial_babylon_public_key",
            "first_seen_at_olympia_state_version",
        ]
    ]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lookup_table_path = f"output/olympia_babylon_addresses_{timestamp}.csv"
    df.to_csv(lookup_table_path, index=False)
    logging.info(
        f"Conversion successfully completed. Output saved to: {lookup_table_path}"
    )


def convert_resources_address():
    csv_file_path = "resources/olympia_resources_addresses.csv"
    df = pd.read_csv(csv_file_path)
    df["babylon_address"] = df["olympia_address"].apply(
        lambda x: derive_babylon_resource_address(x)
    )

    df = df[
        [
            "olympia_gateway_id",
            "olympia_address",
            "babylon_address",
            "first_seen_at_olympia_state_version",
            "supply_fixed",
            "initial_babylon_name",
            "initial_babylon_symbol",
            "initial_babylon_description",
            "initial_babylon_supply",
        ]
    ]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lookup_table_path = f"output/olympia_babylon_resource_addresses_{timestamp}.csv"
    df.to_csv(lookup_table_path, index=False)
    logging.info(
        f"Conversion successfully completed. Output saved to: {lookup_table_path}"
    )


def convert_validators_addresses():
    validators_df = pd.read_csv("resources/validators_addresses.csv")
    olympia_babylon_df = pd.read_csv(
        "resources/olympia_babylon_validators_addresses.csv"
    )

    merged_df = pd.merge(
        validators_df,
        olympia_babylon_df,
        left_on="address",
        right_on="Olympia Address",
        how="inner",
    )

    result_df = merged_df[
        [
            "id",
            "address",
            "Babylon Address",
            "from_state_version",
            "Name",
            "Public Key at Genesis",
            "Stake at migration time",
        ]
    ]

    result_df.columns = [
        "olympia_gateway_id",
        "olympia_address",
        "babylon_address",
        "first_seen_at_olympia_state_version",
        "initial_babylon_name",
        "initial_babylon_public_key",
        "initial_babylon_xrd_staked",
    ]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    result_df.to_csv(f"combined_validators_{timestamp}.csv", index=False)


def create_output_directory():
    output_directory = join(dirname(abspath(__file__)), "output")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logging.info(f"Directory '{output_directory}' created.")
    else:
        logging.info(f"Directory '{output_directory}' already exists.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Olympia addresses or resources to Babylon addresses."
    )
    parser.add_argument(
        "--accounts",
        action="store_true",
        help="Convert Olympia account addresses to Babylon addresses",
    )
    parser.add_argument(
        "--resources",
        action="store_true",
        help="Convert Olympia resource addresses to Babylon addresses",
    )

    args = parser.parse_args()
    if args.accounts:
        logging.info("Converting accounts")
        convert_account_address()
    elif args.resources:
        logging.info("Converting resources")
        convert_resources_address()
    else:
        logging.info("Please specify either --accounts or --resources")


if __name__ == "__main__":
    main()

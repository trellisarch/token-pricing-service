import csv
import argparse
import logging
import os
from os.path import dirname, abspath, join
from datetime import datetime
from radix_engine_toolkit import (
    OlympiaAddress,
    derive_virtual_account_address_from_olympia_account_address,
    derive_resource_address_from_olympia_resource_address
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_account_address():
    csv_file_path = 'resources/olympia_accounts_addresses.csv'
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        data = list(csv_reader)

    data[0]['babylon_address'] = 'babylon_address'

    for row in data[1:]:  # Skip the header row
        olympia_address = OlympiaAddress(row["address"])
        babylon_address = derive_virtual_account_address_from_olympia_account_address(
            network_id=1,
            olympia_account_address=olympia_address
        )

        row['babylon_address'] = babylon_address.as_str()

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    lookup_table_path = f'output/olympia_babylon_addresses_{timestamp}.csv'
    with open(lookup_table_path, 'w', newline='') as file:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)
    logging.info(
        f"Conversion successfully completed. Output saved to: {lookup_table_path}")


def convert_resources_address():
    csv_file_path = 'resources/olympia_resources_addresses.csv'
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        data = list(csv_reader)

    data[0]['babylon_resource_address'] = 'babylon_resource_address'

    for row in data[1:]:  # Skip the header row
        olympia_resource_address = OlympiaAddress(row["rri"])
        babylon_resource_address = derive_resource_address_from_olympia_resource_address(
            network_id=1,
            olympia_resource_address=olympia_resource_address
        )

        row['babylon_resource_address'] = babylon_resource_address.as_str()

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    lookup_table_path = f'resources/olympia_babylon_resources_{timestamp}.csv'
    with open(lookup_table_path, 'w', newline='') as file:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)
    logging.info(
        f"Conversion successfully completed. Output saved to: {lookup_table_path}")


def create_output_directory():
    output_directory = join(dirname(abspath(__file__)), "output")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        logging.info(f"Directory '{output_directory}' created.")
    else:
        logging.info(f"Directory '{output_directory}' already exists.")


def main():
    parser = argparse.ArgumentParser(description='Convert Olympia addresses or resources to Babylon addresses.')
    parser.add_argument('--accounts', action='store_true',
                        help='Convert Olympia account addresses to Babylon addresses')
    parser.add_argument('--resources', action='store_true',
                        help='Convert Olympia resource addresses to Babylon addresses')

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

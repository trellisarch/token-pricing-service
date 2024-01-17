import csv
from radix_engine_toolkit import (
    OlympiaAddress,
    derive_virtual_account_address_from_olympia_account_address
)


def convert():
    csv_file_path = 'resources/olympia_addresses.csv'
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

    lookup_table_path = 'resources/olympia_babylon_addresses.csv'
    with open(lookup_table_path, 'w', newline='') as file:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


if __name__ == "__main__":
    convert()
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests


def test_convertion():
    df = pd.read_csv("resources/olympia_babylon_addresses.csv", skiprows=1)
    api_url = "https://mainnet.radixdlt.com/state/entity/details"
    max_threads = 10

    def send_request(addresses):
        request_body = {"addresses": addresses}
        response = requests.post(api_url, json=request_body)
        return response.status_code

    batches = [[row["babylon_address"]] for _, row in df.iterrows()]
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(send_request, batch): batch for batch in batches}
        for future in as_completed(futures):
            batch = futures[future]
            try:
                status_code = future.result()
                if status_code != 200:
                    print(f"Batch failed with status code {status_code}: {batch}")
                    break

            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_convertion()

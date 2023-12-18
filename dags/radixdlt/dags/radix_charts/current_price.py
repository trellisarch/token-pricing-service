import logging
from datetime import datetime

import psycopg2
import requests
from airflow import DAG
from airflow.decorators import task

from radixdlt.config.config import Config
from radixdlt.lib.http import get_headers

with DAG(dag_id="radix_charts_current_price",
         start_date=datetime(2023, 12, 17),
         schedule="0 0 * * *") as dag:

    @task()
    def get_tokens_current_price():
        token_list = requests.get(Config.RADIX_CHARTS_TOKENS_PRICE_LIST,
                                  headers=get_headers()).json()["data"]
        logging.info(token_list)
        resources = []
        for resource_address in token_list.keys():
            resources.append(resource_address)
        resources_chunks = [resources[i:i + 30] for i in range(0, len(resources), 30)]

        tokens = []
        for chunk in resources_chunks:
            resources_addresses = ','.join(chunk)
            token_prices = requests.get(
                f"{Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT}={resources_addresses}",
                headers=get_headers()
            ).json()["data"]
            token_list = [value for _, value in token_prices.items()]
            for token in token_list:
                tokens.append(token)
        logging.info(tokens)

        # for token in tokens:
        #     try:
        #         conn = psycopg2.connect(
        #             dbname='radix_data',
        #             user='radix',
        #             password='radix',
        #             host='postgres_radix'
        #         )
        #         cursor = conn.cursor()
        #         cursor.execute(
        #             "INSERT INTO radix_tokens (timestamp, token_name, usd_market_cap, usd_vol_24h, usd_price) "
        #             "VALUES (%s, %s, %s, %s, %s)",
        #             (datetime.now().isoformat(),
        #              token["name"],
        #              token["usd_market_cap"],
        #              token["usd_vol_24h"],
        #              token["usd_price"])
        #         )
        #
        #         conn.commit()
        #
        #     except psycopg2.Error as e:
        #         print("Error occurred while inserting data:", e)

    get_tokens_current_price()

from os import getenv

import psycopg2


def get_postgres_connection():
    return psycopg2.connect(
        dbname=getenv("DB_NAME", "token_price"),
        user=getenv("DB_USER", "postgres"),
        password=getenv("DB_PASSWORD", "postgres"),
        host=getenv("DB_HOST", "airflow-postgresql"),
    )

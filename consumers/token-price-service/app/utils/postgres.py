import psycopg2
from os import getenv


def get_postgres_connection():
    return psycopg2.connect(
        dbname=getenv("DB_NAME", "postgres"),
        user=getenv("DB_USER", "postgres"),
        password=getenv("DB_PASSWORD", "postgres"),
        host=getenv("DB_HOST", "localhost"),
    )

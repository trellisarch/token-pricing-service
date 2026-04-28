"""Create the DAGs database and grant permissions if needed."""
import os
import sys
from urllib.parse import urlparse

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def main():
    db_uri = os.environ["DB_URI"]
    parsed = urlparse(db_uri)

    host = parsed.hostname
    port = parsed.port or 5432
    password = parsed.password
    username = "postgres"
    db_name = "dags"

    print(f"Checking if the database exists. Connecting to {host} with user {username}")

    conn = psycopg2.connect(host=host, port=port, user=username, password=password, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if cur.fetchone():
        print("Database already exists. Skipping creation.")
    else:
        print("Creating new database...")
        cur.execute(f"CREATE DATABASE {db_name}")

    cur.close()
    conn.close()

    conn = psycopg2.connect(host=host, port=port, user=username, password=password, dbname=db_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    print("Granting permissions...")
    cur.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username}")

    cur.close()
    conn.close()

    print("Database setup complete.")


if __name__ == "__main__":
    main()

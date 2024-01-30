#!/bin/bash
set -x

# Extracting components from DB_URI
DB_USERNAME=$(echo $DB_URI | awk -F[/:] '{print $4}')
DB_PASSWORD=$(echo $DB_URI | awk -F[@/] '{print $3}')
DB_HOST=$(echo $DB_URI | awk -F[@/] '{print $4}')
DB_NAME=$(echo $DB_URI | awk -F[/] '{print $NF}' | awk -F[?] '{print $1}')

DB_USERNAME="postgres"
DB_NAME="dags"

echo "Checking if the database exists. Connecting to $DB_HOST with user $DB_USER"
DB_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -lqt | cut -d \| -f 1 | grep -w $DB_NAME)

if [ -z "$DB_EXISTS" ]; then
    echo "Creating new database..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -c "CREATE DATABASE $DB_NAME;"
else
    echo "Database already exists. Skipping creation."
fi

echo "Granting permissions..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USERNAME;"

echo "Database setup complete."

alembic upgrade head

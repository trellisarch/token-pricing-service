#!/bin/bash
DB_USERNAME="postgres"
DB_NAME="dags"

echo "Checking if the database exists..."
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

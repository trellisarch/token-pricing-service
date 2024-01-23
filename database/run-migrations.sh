#!/bin/bash
DB_USERNAME="postgres"
DB_NAME="dags"

echo "Dropping existing database..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "Creating new database..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -c "CREATE DATABASE $DB_NAME;"

echo "Granting permissions..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U $DB_USERNAME -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USERNAME;"

echo "Database setup complete."

alembic upgrade head

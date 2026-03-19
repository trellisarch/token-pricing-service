# Local Environment Setup

## Prerequisites

- Docker & Docker Compose
- uv (Python package manager)
- psql (PostgreSQL client)

## 1. Build Docker Images

From the repo root:

```bash
docker build -t migrations database -f database/Dockerfile
docker build -t local-airflow airflow -f airflow/Dockerfile
```

## 2. Start Containers

```bash
docker compose -f airflow/docker-compose.yml up
```

## 3. Run Database Migrations

In a new terminal, change to the database directory:

```bash
cd database
```

Set up the Python environment (first time only):

```bash
uv venv --python 3.11.10
source .venv/bin/activate
uv pip install -r requirements.txt
```

Find the exposed port for the Airflow PostgreSQL container (from the repo root):

```bash
docker compose -f airflow/docker-compose.yml port airflow-postgresql 5432
```

Set the database connection using the exposed port (e.g. if the above returns `0.0.0.0:5433`):

```bash
export DB_URI="postgresql://postgres:postgres@localhost:<exposed_port>/dags"
```

Check the current migration head:

```bash
uv run alembic current
```

Run migrations:

```bash
uv run alembic upgrade head
```

Verify tables were created:

```bash
psql -h localhost -p <exposed_port> -U postgres -d dags
```

> **Note**: Airflow uses a separate PostgreSQL container (`airflow-postgresql`) with database `dags`, not the default `localhost:5432/postgres`.

## 4. Access Airflow UI

Open http://localhost:8080/dags

- **Username**: airflow
- **Password**: airflow

## Cleaning Up Data

To stop all containers and remove PostgreSQL volumes (wipes all data):

```bash
docker compose -f airflow/docker-compose.yml down -v
```

After bringing containers back up, re-run migrations:

```bash
docker compose -f airflow/docker-compose.yml up -d
cd database
uv run alembic upgrade head
```

## Creating a New Migration

From the `database` directory:

```bash
uv run alembic current
uv run alembic revision -m "description of change"
```

Edit the generated file in `migrations/versions/`, then apply:

```bash
uv run alembic upgrade head
```
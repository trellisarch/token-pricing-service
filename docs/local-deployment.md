# Local Deployment Guide

## Prerequisites

- Docker and Docker Compose
- At least 4 GB of RAM allocated to Docker
- At least 2 CPUs allocated to Docker

## Architecture

The local stack runs the following services:

| Service | Description | Port |
|---------|-------------|------|
| `airflow-webserver` | Airflow UI | `localhost:8080` |
| `airflow-scheduler` | DAG scheduler | - |
| `airflow-worker` | Celery worker | - |
| `airflow-triggerer` | Async trigger handler | - |
| `postgres_airflow` | Airflow metadata DB | `localhost:5532` |
| `airflow-postgresql` | DAGs application DB | `localhost:5533` |
| `redis` | Celery broker | - |
| `migrations` | DB schema migrations | - |

## Active DAGs

| DAG | Description |
|-----|-------------|
| `ledger_current_price` | Fetches token prices from Radix ledger DEX pools with CoinGecko-weighted pricing |
| `watchdog` | Health check DAG |
| `acc_comp_monitoring` | Account component balance monitoring with Slack alerts |

## Getting Started

### 1. Build the migration image

From the repo root:

```bash
cd database
docker build -t migrations .
cd ..
```

### 2. Build and start Airflow

```bash
cd airflow
docker compose up --build -d
```

This will:
- Build the Airflow image from `airflow/Dockerfile`
- Start PostgreSQL (x2), Redis, and all Airflow services
- Run DB migrations via the `migrations` service
- Initialize Airflow with a default admin user

### 3. Wait for services to be healthy

```bash
docker compose ps
```

Wait until all services show `healthy` status. The initial startup takes 1-2 minutes.

### 4. Access the Airflow UI

Open http://localhost:8080 and log in:

- **Username**: `airflow`
- **Password**: `airflow`

### 5. Unpause DAGs

All DAGs are paused by default. In the Airflow UI, toggle on the DAGs you want to test:

- `ledger_current_price` - requires network access to Radix Gateway and CoinGecko
- `watchdog` - runs independently
- `acc_comp_monitoring` - requires `ACC_COMP_MONITORING_SLACK_WEBHOOK_URL` to send alerts

## Configuration

Environment variables are set in `airflow/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRFLOW_UID` | `502` | User ID in Airflow containers (use `id -u` on Linux) |
| `COIN_GECKO_API` | `https://api.coingecko.com/api/v3` | CoinGecko free API base URL |
| `NETWORK_ID` | `1` | Radix network (1=mainnet, 2=stokenet) |

Additional env vars can be added to `airflow/.env` or set inline:

```bash
ACC_COMP_MONITORING_SLACK_WEBHOOK_URL=https://hooks.slack.com/... docker compose up -d
```

See `airflow/dags/radixdlt/config/config.py` for all available configuration options.

## Connecting to the DAGs database

The databases are exposed on non-standard ports to avoid conflicts with local PostgreSQL:

```bash
# DAGs application database
psql postgresql://postgres:postgres@localhost:5533/dags

# Airflow metadata database
psql postgresql://airflow:airflow@localhost:5532/airflow
```

## Viewing logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f airflow-scheduler

# DAG task logs are also available in the Airflow UI under each task instance
```

## Stopping

```bash
cd airflow
docker compose down
```

To also remove the database volumes (full reset):

```bash
docker compose down -v
```

## Troubleshooting

**Containers keep restarting**: Check Docker has enough memory (`docker stats`). Airflow needs at least 4 GB.

**DAG import errors**: Check the scheduler logs (`docker compose logs airflow-scheduler`). Common causes are missing Python dependencies in `requirements.txt`.

**CoinGecko rate limiting**: The free tier allows ~10-15 requests/minute without an API key. The `ledger_current_price` DAG makes 1 call/minute, which is within limits.

**Database connection errors**: Ensure both PostgreSQL containers are healthy before the scheduler starts. Run `docker compose ps` to check.

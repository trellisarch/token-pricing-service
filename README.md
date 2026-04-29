# Radix Airflow


## Overview

This project employs Apache Airflow to fetch token prices from Radix ledger DEX pools and CoinGecko, storing them in a PostgreSQL database. The data powers the Token Price Service used by the Radix wallet.

## Active DAGs

- **ledger_current_price**: Fetches token prices from Radix ledger DEX pools with CoinGecko-weighted pricing for major tokens.
- **watchdog**: Health-check DAG that monitors Airflow scheduler liveness.
- **acc_comp_monitoring**: Monitors account component balances on the Radix network and sends Slack alerts on threshold breaches.

## Components

### Apache Airflow

- Manages data ingestion from Radix Gateway and CoinGecko APIs.
- Orchestrates data pipelines and scheduling.

### PostgreSQL

- Acts as the central repository for ingested data.
- Stores token prices for the Token Price Service.

### Token Price Service

- Consumes PostgreSQL data for Radix wallet functionalities.
- Provides token price endpoints.

## Setup and Configuration

See [docs/ledger_prices.md](docs/ledger_prices.md) for detailed documentation on the ledger pricing DAG and consumer service.

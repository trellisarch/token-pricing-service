# Radix Airflow

## Overview

This project employs Apache Airflow to gather data from multiple APIs such as Coingecko, Radix Charts, YouTube, Telegram, X, etc. The ingested data is then stored in a PostgreSQL database. This stored information serves two primary purposes:

- **Dashboard Creation**: Utilizing PostgreSQL data to generate dashboards via either Grafana or Metabase.
- **Token Price Service**: A service named `token_price_service` consumes PostgreSQL data, providing functionality for the Radix wallet.

## Workflow Diagram

![Workflow Diagram](link-to-your-diagram)

## Components

### Apache Airflow

- Manages data ingestion from various APIs.
- Orchestrates data pipelines and scheduling.

### PostgreSQL

- Acts as the central repository for ingested data.
- Stores information for further utilization.

### Dashboarding Tool (Grafana/Metabase)

- Utilizes PostgreSQL data to create visual dashboards.
- Offers insights and analytics based on stored information.

### Token Price Service

- Consumes PostgreSQL data for Radix wallet functionalities.
- Provides essential token-related services.

## Setup and Configuration


# Radix Charts DAGs

The radix_charts subsystem fetches token metadata and prices from the Radix Charts API, stores them in PostgreSQL, and feeds an oracle price pipeline.

## Architecture

```
Radix Charts API
    │
    ├──[tokens_list DAG]──→ radix_tokens table (token metadata)
    │
    ├──[current_price DAG]──→ radix_token_prices (historical)
    │                     └──→ radix_token_prices_latest (upsert)
    │                          └──→ latest_token_prices (materialized view)
    │
    └──[oracle DAG via RadixChartsPriceProvider]
           ├── Calculate {symbol}/XRD pairs
           ├── Validate against CoinGecko (+/-5%)
           └── Submit to blockchain oracle
```

## DAGs

### `radix_charts_tokens_list`

**File**: `airflow/dags/radixdlt/dags/radix_charts/tokens_list.py`

Maintains the master list of tokens by syncing with the Radix Charts API. Uses classic Airflow DAG style with `PythonOperator` tasks.

**Tasks** (linear dependency):

1. **`fetch_tokens`** — GETs `Config.RADIX_CHARTS_TOKENS_PRICE_LIST` with bearer auth headers. Parses `response.json()["data"]` and pushes to XCom.
2. **`insert_tokens`** — Pulls XCom from `fetch_tokens`, calls `RadixToken.insert_tokens(tokens)`.

**Token insertion logic** (`models/radix_charts/token.py`):

- API returns tokens keyed by `resource_address` with `symbol` and `name` fields.
- Tokens present in the API response are marked `allowlist=True`.
- Tokens in the DB but absent from the API response are marked `allowlist=False` (delisted).
- New tokens are inserted with `allowlist=True`.

**Table**: `radix_tokens` — columns: `id`, `resource_address` (unique), `symbol`, `name`, `allowlist`.

### `radix_charts_current_price`

**File**: `airflow/dags/radixdlt/dags/radix_charts/current_price.py`

Fetches current USD prices for all known tokens and writes them to two tables. Uses the modern `@dag` / `@task` decorator pattern.

**Single task**:

1. **`fetch_tokens_price_task`** — Loads token list from the **database** via `RadixToken.list_tokens()` (queries `radix_tokens` where `allowlist=True`), then calls `PriceFetcher.fetch_and_save_prices(tokens)`.

**Price fetching logic** (`models/radix_charts/token_price.py` — `PriceFetcher`):

- Chunks tokens into batches of 30 (API limit).
- For each batch, GETs `Config.RADIX_CHARTS_TOKEN_PRICE_CURRENT` with `resource_addresses` query param.
- For each token in the response:
  - **Appends** a row to `radix_token_prices` (historical, append-only).
  - **Upserts** into `radix_token_prices_latest` using PostgreSQL `ON CONFLICT (resource_address) DO UPDATE`.
  - Converts `last_updated_at` from Unix timestamp to `datetime`.
- After all batches, commits and attempts to `REFRESH MATERIALIZED VIEW CONCURRENTLY latest_token_prices` (rolls back on failure without blocking the main commit).

**Implicit dependency**: The `tokens_list` DAG must run first to seed the `radix_tokens` table. There is no explicit cross-DAG dependency — both share the same schedule (`Config.TOKEN_PRICE_SCHEDULE_INTERVAL`).

## Database Tables

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `radix_tokens` | Master token list | `resource_address` (unique), `symbol`, `name`, `allowlist` |
| `radix_token_prices` | Historical prices (append-only) | `resource_address`, `usd_price`, `usd_market_cap`, `usd_vol_24h`, `last_updated_at` |
| `radix_token_prices_latest` | Current snapshot (upserted) | Same as above, `resource_address` is unique |
| `latest_token_prices` | Materialized view | Refreshed after price inserts |

## Library: `RadixChartsPriceProvider`

**File**: `airflow/dags/radixdlt/lib/radix_charts.py`

Used by the oracle DAG (`dags/radixdlt/oracle.py`) — not a standalone DAG.

- Fetches prices for a configured subset of tokens (`Config.RADIX_CHARTS_ORACLE_TOKENS` = `"hug,defiplaza,floop,radix"`).
- Looks up resource addresses from `lib/const.py` → `RADIX_CHARTS_TOKENS` dict.
- Calculates XRD-denominated pairs: `{symbol}/XRD = symbol_usd_price / xrd_usd_price`.
- Extends `BasePriceProvider` (abstract base in `lib/price_provider.py`).

**Price validation** (`validate_prices()`):

- Compares Radix Charts prices against CoinGecko prices.
- Tolerance: +/-5% (`Config.ORACLE_PRICE_DIFF_TRIGGER`).
- Only passes through prices within the tolerance band.

**StatsD metrics** (`add_statsd_metrics()`):

- `dag_oracle.radixchart.fetch.{symbol}.passed/failed` — per-token fetch status
- `dag_oracle.radixchart.passed/failed` — overall API call status
- `oracle.radixcharts.request_time` — request duration

## Shared Infrastructure

| Component | File | Role |
|-----------|------|------|
| Config | `config/config.py` | Centralized env-var-driven config for API URLs, schedule intervals, auth tokens, StatsD client |
| DB session | `models/base.py` | `get_session()` creates SQLAlchemy sessions from `Config.DB_URI` |
| HTTP headers | `lib/http.py` | `get_radix_charts_headers()` adds bearer token from `RADIX_CHARTS_AUTHORIZATION_TOKEN` env var |
| Token constants | `lib/const.py` | `RADIX_CHARTS_TOKENS` dict mapping token names to `{resource_address, symbol}` |
| Price provider base | `lib/price_provider.py` | `BasePriceProvider` abstract class requiring `process_prices()` |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `TOKEN_PRICE_SCHEDULE_INTERVAL` | Cron schedule for both DAGs | `None` (disabled) |
| `RADIX_CHARTS_AUTHORIZATION_TOKEN` | Bearer token for API auth | Required |
| `DB_URI` | PostgreSQL connection string | `sqlite:///app.db` |
| `COIN_GECKO_API_KEY` | For price validation | Optional |
| `STATSD_HOST` | StatsD host | `airflow-statsd` |
| `STATSD_EXPORTER_INGEST_PORT` | StatsD port | `9125` |

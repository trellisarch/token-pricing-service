# Ledger Prices DAG

Fetches token prices directly from the Radix ledger by calling `get_price` (C9) or `price_sqrt` (Ociswap) on DEX pool components via the Gateway `/transaction/preview` endpoint. Prices are converted to USD using hUSDC as a proxy and averaged across all whitelisted pools per token.

## Architecture

```
Radix Gateway API (/transaction/preview)
    │
    └──[ledger_current_price DAG]
           ├── Fetch XRD/hUSDC rate (USD proxy)
           ├── For each token, fetch price from all whitelisted pools
           ├── Average across pools, log per-pool prices
           └── Write to ledger_token_prices (historical) + ledger_token_prices_latest (upsert)
                  │
                  └── Token-price-service consumer reads via POST /price/ledger-tokens
```

## DAG: `ledger_current_price`

**File**: `airflow/dags/radixdlt/dags/ledger_prices/current_price.py`

**Schedule**: `Config.LEDGER_PRICE_SCHEDULE_INTERVAL` (env var, default `None`).

**Single task**: `fetch_prices_task` calls `LedgerPriceFetcher.fetch_and_save_prices(LEDGER_TOKENS)`.

### Price calculation

1. Fetch XRD/hUSDC rate from `LEDGER_USD_POOL` (C9 pool) — this is the XRD USD price.
2. **XRD**: `usd_price` = XRD/hUSDC rate directly.
3. **hUSDC**: `usd_price` = 1.0 (stablecoin).
4. **Other tokens**: For each pool, `usd_price = xrd_usd_price / pool_price`. Average across all pools. Per-pool prices are logged but not stored.

### Supported DEXes

- **C9**: Calls `get_price` on the pool component.
- **Ociswap**: Calls `price_sqrt`, then squares the result.

## Token Configuration

**File**: `airflow/dags/radixdlt/lib/const.py` — `LEDGER_TOKENS`

Static/hardcoded dict. Each token has:
- `resource_address` — used as the DB key and for consumer API queries
- `pools` — list of `{component, dex}` entries (one or many)
- `base` / `quote` — all XRD-based pairs

Current tokens: XRD, FLOOP (C9 + Ociswap pools), hUSDC (C9 pool).

## Database Tables

| Table | Purpose | Key columns |
|-------|---------|-------------|
| `ledger_token_prices` | Historical (append-only) | `resource_address`, `usd_price`, `last_updated_at` |
| `ledger_token_prices_latest` | Current snapshot (upsert) | Same columns, `resource_address` is unique |

Schema mirrors `radix_token_prices` / `radix_token_prices_latest` so both DAGs can run in parallel.

## Consumer API

**Endpoint**: `POST /price/ledger-tokens`

**Request**: Same `TokenPricesRequest` schema — `{"currency": "USD", "tokens": ["resource_rdx1..."]}`

**Response**: Same `TokenPricesResponse` schema with `TokenPrice` objects.

Queries `ledger_token_prices_latest` by `resource_address` (no allowlist filter — token list is static).

## Files

| File | Purpose |
|------|---------|
| `airflow/dags/radixdlt/dags/ledger_prices/current_price.py` | DAG definition |
| `airflow/dags/radixdlt/models/ledger_prices/token_price.py` | DB models + `LedgerPriceFetcher` |
| `airflow/dags/radixdlt/lib/ledger.py` | Gateway interaction (epoch, preview, price extraction) |
| `airflow/dags/radixdlt/lib/const.py` | `LEDGER_TOKENS`, `LEDGER_USD_POOL` |
| `airflow/dags/radixdlt/config/config.py` | `LEDGER_PRICE_SCHEDULE_INTERVAL` |
| `consumers/token-price-service/app/models/token_price.py` | `LedgerTokenPriceLatest` model |
| `consumers/token-price-service/app/api/price.py` | `/price/ledger-tokens` endpoint |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LEDGER_PRICE_SCHEDULE_INTERVAL` | Cron schedule for the DAG | `None` (disabled) |
| `NETWORK_GATEWAY` | Radix Gateway URL | `https://mainnet.radixdlt.com` |
| `DB_URI` | PostgreSQL connection string | `sqlite:///app.db` |

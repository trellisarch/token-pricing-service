# Ledger Prices DAG

Fetches token prices from the Radix ledger and CoinGecko. Major tokens (XRD, hETH, xETH, hWBTC, xWBTC, hSOL, xUSDT, xUSDC, hUSDC, hBNB) use an 80/20 weighted average of CoinGecko and ledger DEX prices. All other tokens use 100% ledger DEX prices. Prices are view-only for the Radix wallet — not used for swaps.

## Architecture

```
CoinGecko API (/simple/price)
    │                              Radix Gateway API (/transaction/preview)
    │                                  │
    └──────────────┬───────────────────┘
                   │
           [ledger_current_price DAG]
           ├── Fetch XRD/hUSDC rate from C9 pool (USD baseline for all tokens)
           ├── Fetch CoinGecko USD prices for mapped tokens
           ├── For each token:
           │     ├── CoinGecko-mapped: 80% CoinGecko + 20% ledger (configurable)
           │     └── Others: 100% ledger, averaged across pools
           ├── Fallback: cached CoinGecko price (5min window) → 100% ledger
           ├── Safety: reject CoinGecko if >50% divergence from ledger
           └── Write to ledger_token_prices (historical) + ledger_token_prices_latest (upsert)
                  │
                  └── Token-price-service consumer reads via POST /price/ledger-tokens
```

## DAG: `ledger_current_price`

**File**: `airflow/dags/radixdlt/dags/ledger_prices/current_price.py`

**Schedule**: `Config.LEDGER_PRICE_SCHEDULE_INTERVAL` (env var, default `None`).

**Single task**: `fetch_prices_task` calls `LedgerPriceFetcher.fetch_and_save_prices(LEDGER_TOKENS)`.

### Price calculation

1. Fetch XRD/hUSDC rate from `LEDGER_USD_POOL` (C9 pool) — this is the on-chain USD baseline for converting all token prices.
2. Fetch CoinGecko USD prices for all mapped tokens in a single API call.
3. **CoinGecko-mapped tokens** (XRD, hETH, xETH, hWBTC, xWBTC, hSOL, xUSDT, xUSDC, hUSDC, hBNB):
   - Compute ledger price from on-chain DEX pools as before
   - `usd_price = (coingecko_weight × coingecko_price) + ((1 - coingecko_weight) × ledger_price)`
   - Default weight: 80% CoinGecko / 20% ledger, configurable per token
   - **XRD note**: the CoinGecko-weighted price is only stored for XRD's own row. The on-chain hUSDC/XRD rate remains the baseline for converting other tokens to USD.
4. **Other tokens**: For each pool, `usd_price = xrd_usd_price / pool_price`. Average across all pools. Per-pool prices are logged but not stored.

### CoinGecko mapping

| Token(s) | CoinGecko ID | Default weight (CG/ledger) |
|----------|-------------|---------------------------|
| XRD | `radix` | 80/20 |
| hETH, xETH | `ethereum` | 80/20 |
| hWBTC, xWBTC | `bitcoin` | 80/20 |
| hSOL | `solana` | 80/20 |
| xUSDT | `tether` | 80/20 |
| xUSDC, hUSDC | `usd-coin` | 80/20 |
| hBNB | `binancecoin` | 80/20 |

### Fallback strategy

When CoinGecko is unavailable (API down, rate-limited, error):

1. Use last successful CoinGecko price if within **5-minute** staleness window (configurable via `COINGECKO_STALENESS_THRESHOLD_SECS`).
2. Beyond 5 minutes, fall back to **100% ledger price**.
3. Cache is tracked via `price_source` and `fetched_at` columns on `ledger_token_prices_latest`.

### Divergence safety

If CoinGecko and ledger prices diverge by more than **50%** (configurable via `COINGECKO_DIVERGENCE_THRESHOLD`), the CoinGecko price is rejected and the cached CoinGecko price is used instead. This guards against CoinGecko API glitches.

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
| `ledger_token_prices_latest` | Current snapshot (upsert) | `resource_address` (unique), `usd_price`, `last_updated_at`, `price_source`, `fetched_at` |

New columns on `ledger_token_prices_latest`:
- `price_source` — indicates how the price was derived (e.g., `coingecko_weighted`, `ledger_only`, `coingecko_cached`)
- `fetched_at` — timestamp of the last successful CoinGecko fetch for this token (used for staleness checks)

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
| `airflow/dags/radixdlt/lib/coingecko.py` | `GeckoPriceProvider` — CoinGecko API integration |
| `airflow/dags/radixdlt/lib/const.py` | `LEDGER_TOKENS`, `LEDGER_USD_POOL` |
| `airflow/dags/radixdlt/config/config.py` | `LEDGER_PRICE_SCHEDULE_INTERVAL`, CoinGecko config |
| `consumers/token-price-service/app/models/token_price.py` | `LedgerTokenPriceLatest` model |
| `consumers/token-price-service/app/api/price.py` | `/price/ledger-tokens` endpoint |

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LEDGER_PRICE_SCHEDULE_INTERVAL` | Cron schedule for the DAG | `None` (disabled) |
| `NETWORK_GATEWAY` | Radix Gateway URL | `https://mainnet.radixdlt.com` |
| `DB_URI` | PostgreSQL connection string | `sqlite:///app.db` |
| `COIN_GECKO_API` | CoinGecko API base URL | `https://api.coingecko.com/api/v3` |
| `COINGECKO_STALENESS_THRESHOLD_SECS` | Max age of cached CoinGecko price before ledger fallback | `300` (5 min) |
| `COINGECKO_DIVERGENCE_THRESHOLD` | Max allowed divergence between CoinGecko and ledger | `0.5` (50%) |

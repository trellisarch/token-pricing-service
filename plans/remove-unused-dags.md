# Plan: Remove Unused DAGs

> Source PRD: GitHub Issue #389

## Architectural decisions

- **DAGs kept**: `ledger_current_price`, `watchdog`, `acc_comp_monitoring`
- **DAGs removed**: 14 DAGs (radix_charts_current_price, radix_charts_tokens_list, oracle_price, coingecko_token_prices, github, network, tokens, reddit, telegram, twitter, youtube, google_play, npm_metrics, crates_io_metrics)
- **Shared modules retained**: `config.py`, `models/base.py`, `models/ledger_prices/`, `models/acc_comp_monitoring/`, `lib/const.py` (trimmed), `lib/coingecko.py`, `lib/price_provider.py`, `lib/ledger.py`, `lib/ret.py`
- **No database migrations**: fresh deployment — orphaned tables won't exist
- **Consumer service**: already updated separately, out of scope

---

## Phase 1: Remove DAG directories

**User stories**: 1, 3

### What to build

Delete the 12 DAG subdirectories containing the 14 removed DAGs. This is the core change that removes all unused DAG definitions from the Airflow deployment.

### Acceptance criteria

- [ ] 12 DAG subdirectories deleted (coingecko_token_prices, crates_io, github, google_play, network, npm, radix_charts, radixdlt, reddit, telegram, twitter, youtube)
- [ ] 3 DAG subdirectories remain (ledger_prices, watchdog, acc_comp_monitoring)
- [ ] Airflow DAG integrity test passes for kept DAGs

---

## Phase 2: Remove unused models

**User stories**: 9

### What to build

Delete the 12 model subdirectories that served the removed DAGs. Keep base.py, ledger_prices/, and acc_comp_monitoring/.

### Acceptance criteria

- [ ] 12 model subdirectories deleted (coingecko_api, crates_io, github, google_play, network, npm, oracles, radix_charts, reddit, telegram, twitter, youtube)
- [ ] models/base.py, models/ledger_prices/, models/acc_comp_monitoring/ remain
- [ ] No broken imports in kept DAGs

---

## Phase 3: Remove unused libs and strip constants

**User stories**: 5, 8

### What to build

Delete 7 library files only used by removed DAGs. Strip unused constants (RADIX_CHARTS_TOKENS, ORACLE_CMC_PAIRS, ORACLE_COIN_GECKO_IDS) from const.py.

### Acceptance criteria

- [ ] 7 lib files deleted (cmc.py, c9.py, pyth.py, radix_charts.py, oracle.py, gateway.py, http.py)
- [ ] const.py retains only LEDGER_TOKENS, LEDGER_USD_POOL, COINGECKO_MAPPING and related constants
- [ ] coingecko.py, price_provider.py, ledger.py, ret.py remain functional

---

## Phase 4: Clean up config, tests, and scripts

**User stories**: 4, 10

### What to build

Remove dead environment variable references from config.py. Delete test files for removed DAGs. Remove unused utility scripts.

### Acceptance criteria

- [ ] config.py only contains entries used by kept DAGs
- [ ] Tests for removed DAGs deleted (test_coingecko_model, test_crates_io_model, test_npm_metrics)
- [ ] Unused scripts deleted (stats_cmc, stats_pyth, chart)
- [ ] test_dag_integrity.py and test_ledger.py remain
- [ ] Kept DAGs still reference valid config entries

---

## Phase 5: Clean up Helm alerts, docs, and README

**User stories**: 2, 6, 7, 11

### What to build

Remove Prometheus alert rules for deleted DAGs. Delete docs/radix_charts.md. Update README to remove oracle/removed DAG references.

### Acceptance criteria

- [ ] OracleTaskFailure, RadixChartsCurrentPriceTaskFailure, OraclePriceDAGFailure alerts removed
- [ ] General catch-all alert expressions updated (remove oracle/radix_charts exclusions)
- [ ] docs/radix_charts.md deleted
- [ ] README.md updated — no references to removed DAGs
- [ ] docs/ledger_prices.md retained

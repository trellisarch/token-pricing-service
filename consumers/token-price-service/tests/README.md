# Token Price Service Tests

## Prerequisites

```bash
cd consumers/token-price-service
pip install pytest requests locust
```

## Unit Tests

Mocked tests that don't require a running service or database.

```bash
pytest tests/unit/ -v
```

## API Integration Tests

These tests run against a live token-price-service instance.

### Against local docker-compose

Start the service locally first (see [local deployment guide](../../docs/local-deployment.md)), then:

```bash
API_URL=http://localhost:8000 pytest tests/api/test_token_price_service.py -v
```

Note: `test_historical_price` requires the `API_KEY` environment variable to be set.

### Against a deployed environment

```bash
API_URL=https://token-price-service.radixdlt.com API_KEY=<your-key> pytest tests/api/ -v
```

## Performance Tests

Load tests using [Locust](https://locust.io/).

```bash
# All endpoints (tokens + prices + LSUs)
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Token prices only (no LSUs)
locust -f tests/performance/locustfile_price_only_tokens.py --host=http://localhost:8000

# Prices with LSUs
locust -f tests/performance/locustfile_price_only_lsus.py --host=http://localhost:8000
```

Open http://localhost:8089 to configure and start the load test.

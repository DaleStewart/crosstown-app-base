# Tests — Extension 09

## How to run

```bash
# From the repo root — no live Postgres required
pytest docs/extensions/09_postgres_target/tests/ -v
```

## Expected state before completing the extension

All tests **fail** — `query_legacy_db` does not exist in `apps.log_analyst.tools` yet.

## Expected state after completing the extension

All tests pass. The tests use an in-memory SQLite database seeded from
`fixtures/schema.sql` — a live Postgres instance is **not** required.

## Running against real Postgres (optional integration test)

```bash
ENABLE_POSTGRES_TOOL=true \
POSTGRES_HOST=<your-server>.postgres.database.azure.com \
POSTGRES_DB=railops \
POSTGRES_USER=<user> \
POSTGRES_PASSWORD=<password> \
pytest docs/extensions/09_postgres_target/tests/ -v -m "integration"
```

## Dependencies

```
pytest
pytest-asyncio
httpx
```

No `psycopg2` needed for the unit tests (SQLite fallback is used automatically).

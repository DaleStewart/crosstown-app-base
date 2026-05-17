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


## 🐘 Test coverage health

| Metric | Status |
|--------|--------|
| Failing tests in place | [██████████] 100% |
| Test fixture coverage | [██████████] 100% |
| Citation contract checked | [██████████] 100% |
| Deterministic runs | [██████████] 100% (no flakes) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Banner (Tester) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When test assertions are updated or new fixtures added |

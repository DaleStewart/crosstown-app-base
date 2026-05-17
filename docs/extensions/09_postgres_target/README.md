# Extension 09 — Postgres Target

**Time:** ~45 min · **Use cases:** #4 (data warehouse), #5 (PCICS) · **Difficulty:** Medium

## What

The skeleton's Bicep infrastructure (`infra/`) already provisions a PostgreSQL Flexible Server
but the connection is never used — it idles. This extension has your team:

1. **Enable the idle Postgres** by setting the connection string environment variables in your
   local `.env` (or `.env.local`) from the Bicep output.
2. **Apply a mock schema migration** using a provided SQL script so the DB has an `incidents`
   table seeded with fictional data.
3. **Add a `query_legacy_db(sql: str)` tool** to the log analyst that executes read-only SQL
   against Postgres using managed identity (locally: a service account password from env).
4. **Gate real DB calls** behind an env var `ENABLE_POSTGRES_TOOL=true` so the unit tests can
   run against an in-memory SQLite stand-in without a live Postgres.

## Why

Use cases #4 and #5 require the agent to query a relational store that holds structured
incident records — beyond what full-text log search can provide. This extension shows how to
add a database-backed tool while keeping the test suite fast and environment-independent.

## Try this

1. **Find the Bicep output.**
   After `azd up` (or check `infra/` for the Postgres resource name), capture:
   ```
   POSTGRES_HOST=<your-server>.postgres.database.azure.com
   POSTGRES_DB=railops
   POSTGRES_USER=<managed-identity-client-id>
   ```
   Add these to `.env.local` (this file is git-ignored).
2. **Run the schema migration.**
   ```bash
   psql "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
     -f docs/extensions/09_postgres_target/fixtures/schema.sql
   ```
   This creates the `incidents` table and inserts three fictional rows for lines L1/L2/L3.
3. **Add the tool.**
   In `apps/log_analyst/tools.py`, add `query_legacy_db(sql: str) -> dict`. When
   `ENABLE_POSTGRES_TOOL` is not set, fall back to an in-memory SQLite with the same schema.
4. **Register the tool** as a POST endpoint at `/tools/query_legacy_db`.
5. **Run the tests** (they use SQLite automatically):
   ```bash
   pytest docs/extensions/09_postgres_target/tests/ -v
   ```

## Prompt Copilot like this

```
1. "In apps/log_analyst/tools.py, add a function called query_legacy_db(sql: str) -> dict.
   If the env var ENABLE_POSTGRES_TOOL is set, connect to Postgres using psycopg2 with
   connection params from env vars POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD.
   Otherwise, connect to an in-memory SQLite database seeded from
   docs/extensions/09_postgres_target/fixtures/schema.sql.
   Execute the sql parameter as a read-only query (reject any statement that is not SELECT).
   Return {rows: [...], citations: ['postgres://incidents']}."

2. "Register query_legacy_db in apps/log_analyst/main.py the same way search_logs is
   registered. The endpoint should be POST /tools/query_legacy_db."

3. "Write a pytest fixture in conftest.py that creates an in-memory SQLite database,
   runs docs/extensions/09_postgres_target/fixtures/schema.sql against it, and monkeypatches
   the query_legacy_db function to use it. This lets tests run without a live Postgres."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/09_postgres_target/tests/ -v
```

All tests **fail** until `query_legacy_db` is implemented. The tests use SQLite and do **not**
require a live Postgres instance.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [08 — Custom Evals](../08_custom_evals/README.md) · _(last extension)_

---

## 🐘 Health at a glance

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Failing tests in place | [██████████] 100% |
| Copilot prompts | [██████████] 100% (3 prompts) |
| Time to complete | 45 min |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Stark (Architect) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When this extension's failing tests are reshaped or a team completes it |


## 🐘 Health at a glance

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Failing tests in place | [██████████] 100% |
| Copilot prompts | [██████████] 100% (3 prompts) |
| Time to complete | 45 min |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Stark (Architect) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When this extension's failing tests are reshaped or a team completes it |

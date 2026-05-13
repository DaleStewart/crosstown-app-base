# Acceptance — Extension 09

You're done when **ALL** of the following are true.

- [ ] `apps/log_analyst/tools.py` contains a callable `query_legacy_db(sql: str) -> dict`.
- [ ] Calling `query_legacy_db("SELECT * FROM incidents")` returns `{"rows": [...], "citations": [...]}` (via the SQLite fallback, no live DB required for this check).
- [ ] `query_legacy_db` rejects non-SELECT statements (returns an error or raises an exception for `DROP TABLE incidents`).
- [ ] `POST /tools/query_legacy_db` with body `{"sql": "SELECT * FROM incidents"}` returns HTTP 200.
- [ ] `ENABLE_POSTGRES_TOOL` env var gates the real Postgres path (unit tests pass without it set).
- [ ] All tests in `tests/` pass (SQLite-based, no live DB needed).
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Start the log analyst (no ENABLE_POSTGRES_TOOL set → SQLite fallback):
   ```bash
   uvicorn apps.log_analyst.main:app --port 8002
   ```
2. Run:
   ```bash
   curl -s -X POST http://localhost:8002/tools/query_legacy_db \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT * FROM incidents"}' | jq .
   ```
   Show the rows from the in-memory SQLite (L1/L2/L3 fictional data).
3. Run:
   ```bash
   curl -s -X POST http://localhost:8002/tools/query_legacy_db \
     -H "Content-Type: application/json" \
     -d '{"sql": "DROP TABLE incidents"}' | jq .
   ```
   Show the error response (non-SELECT rejected).
4. Run `pytest docs/extensions/09_postgres_target/tests/ -v` and show all green.
5. _(Optional)_ Set `ENABLE_POSTGRES_TOOL=true` and the Postgres env vars, re-run the curl,
   and show the same rows coming from the real Azure Postgres.

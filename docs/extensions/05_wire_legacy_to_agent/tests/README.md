# Tests — Extension 05

## How to run

```bash
# From the repo root
pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v
```

## Expected state before completing the extension

All tests **fail** — `query_incidents` is not in `apps.log_analyst.tools`.

## Expected state after completing the extension

All tests pass.

## Notes

The `query_incidents` tool makes an HTTP call to the legacy service. Unit tests mock this call
with `pytest-mock` / `unittest.mock` so you don't need both services running during `pytest`.

## Dependencies

```
pytest
pytest-asyncio
httpx
pytest-mock   # for mocking outbound HTTP calls
```


## 🔌 Test coverage health

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

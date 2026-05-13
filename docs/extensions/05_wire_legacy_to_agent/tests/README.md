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

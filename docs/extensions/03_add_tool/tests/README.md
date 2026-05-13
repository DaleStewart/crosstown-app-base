# Tests — Extension 03

## How to run

```bash
# From the repo root
pytest docs/extensions/03_add_tool/tests/ -v
```

## Expected state before completing the extension

- `test_correlate_lines_exists_in_tools_module` — **fails** (`correlate_lines` not in tools module).
- `test_correlate_lines_returns_citations` — **fails** (import error or attribute missing).
- `test_correlate_lines_endpoint_returns_200` — **fails** (route not registered).
- `test_tool_registry_includes_correlate_lines` — **fails** (registry not updated).

## Expected state after completing the extension

All tests pass.

## Dependencies

```
pytest
pytest-asyncio
httpx
```

# Tests — Extension 01

## How to run

```bash
# From the repo root
pytest docs/extensions/01_add_health_analyst/tests/ -v
```

## Expected state before completing the extension

All tests **fail**. The import `from apps.health_analyst.main import app` raises `ModuleNotFoundError`
because `apps/health_analyst/` does not exist yet.

## Expected state after completing the extension

All tests pass.

## Dependencies

```
pytest
pytest-asyncio
httpx
```

Install with:

```bash
pip install pytest pytest-asyncio httpx
```

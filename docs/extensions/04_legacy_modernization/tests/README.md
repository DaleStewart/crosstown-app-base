# Tests — Extension 04

## How to run

```bash
# From the repo root
pytest docs/extensions/04_legacy_modernization/tests/ -v
```

## Expected state before completing the extension

- `test_legacy_cs_file_exists` — **fails** (`legacy/SampleController.cs` absent).
- `test_legacy_service_module_importable` — **fails** (`apps/legacy_service` absent).
- All route tests — **fail** (service not implemented).

## Expected state after completing the extension

All tests pass.

## Dependencies

```
pytest
pytest-asyncio
httpx
```

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


## 🏗️ Test coverage health

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

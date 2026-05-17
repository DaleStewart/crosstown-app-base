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


## 🩺 Test coverage health

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

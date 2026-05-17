# Tests — Extension 06

## How to run

```bash
# From the repo root
pytest docs/extensions/06_enable_modernize_pr/tests/ -v
```

## Expected state before completing the extension

- `test_workflow_file_exists` — **fails** (`.github/workflows/modernize-pr.yml` absent).
- `test_workflow_has_on_trigger` — **fails** (file absent).
- `test_workflow_dispatch_trigger_defined` — **fails** (file absent or trigger missing).
- `test_no_if_false_guard` — **fails** (file absent or guard present).

## Expected state after completing the extension

All tests pass.

## Dependencies

```
pytest
pyyaml
```

Install with:

```bash
pip install pytest pyyaml
```


## 🤖 Test coverage health

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

# Tests — Extension 08

## How to run

```bash
# Structural checks (this folder)
pytest docs/extensions/08_custom_evals/tests/ -v

# Full eval gate (run after the structural checks pass)
pytest evals/test_eval_gate.py -v
```

## Expected state before completing the extension

- `test_at_least_three_new_scenario_files` — **fails** (no team-authored YAML files yet).
- `test_scenario_files_have_required_fields` — **fails** (no files to validate).
- `test_scenarios_use_only_fictional_lines` — **fails** (no files to validate).

## Expected state after completing the extension

All tests pass. `pytest evals/test_eval_gate.py` also passes.

## Dependencies

```
pytest
pyyaml
```


## 📏 Test coverage health

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

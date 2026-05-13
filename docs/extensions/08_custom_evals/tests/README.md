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

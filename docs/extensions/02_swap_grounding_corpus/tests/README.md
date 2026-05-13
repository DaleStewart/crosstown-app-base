# Tests — Extension 02

## How to run

```bash
# From the repo root
pytest docs/extensions/02_swap_grounding_corpus/tests/ -v
```

## Expected state before completing the extension

- `test_corpus_readme_exists` — **fails** (`data/mock_logs/README.md` not present).
- `test_corpus_has_team_jsonl_files` — **fails** (no team-authored `.jsonl` files yet).
- `test_load_script_version_bumped` — **fails** (version comment still at 1).
- `test_jsonl_entries_are_valid` — **fails** (no files to validate).

## Expected state after completing the extension

All tests pass.

## Dependencies

```
pytest
```

No extra packages needed (uses only stdlib `json`, `re`, `pathlib`).

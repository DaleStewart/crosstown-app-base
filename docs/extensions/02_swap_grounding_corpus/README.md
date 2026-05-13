# Extension 02 — Swap Grounding Corpus

**Time:** ~30 min · **Use cases:** #1 (log analyzer), #4 (data warehouse) · **Difficulty:** Easy

## What

The skeleton ships with a tiny synthetic corpus under `data/mock_logs/`. This extension has your
team **replace that corpus with your own domain-specific synthetic dataset** (still entirely
fictional — use rail lines L1, L2, L3 only) and then re-index it so the Log Analyst's
`search_logs` tool pulls from your new data. No new code is written; the focus is on the
*data pipeline* that feeds the AI Search grounding index.

## Why

Use case #1 requires the Log Analyst to cite real (mock) log entries. Use case #4 imagines
pulling from a larger data-warehouse snapshot. By swapping the corpus you practice the full
"update data → re-index → verify citations" loop that any production AI grounding workflow
demands.

## Try this

1. **Author your synthetic log corpus.**
   Create at least five new `.jsonl` files inside `data/mock_logs/` — one per fictional incident
   (e.g., `L1_signal_fault_2025-11.jsonl`, `L2_scada_timeout_2025-11.jsonl`). Each line is a
   JSON object with keys `timestamp`, `line`, `system`, `message`, `severity`.
2. **Add a README to the corpus folder.**
   Create `data/mock_logs/README.md` that describes your domain (one paragraph). This is checked
   by the test suite.
3. **Bump the index version comment.**
   Open `scripts/load_search_index.py` and change the version comment at the top
   (e.g., `# corpus-version: 1` → `# corpus-version: 2`). This signals a re-index was done.
4. **Re-run the load script.**
   ```bash
   python scripts/load_search_index.py --dry-run
   ```
   Verify it prints the number of documents it would load (should be > the original count).
5. **Confirm the eval suite still passes.**
   ```bash
   pytest evals/ -v
   ```
   If any eval fails, adjust your corpus or fix the eval expectation.

## Prompt Copilot like this

```
1. "Generate 10 synthetic log entries in JSONL format for a fictional rail system. Each entry
   must have keys: timestamp (ISO 8601), line (one of L1, L2, L3), system (e.g. 'signal',
   'SCADA', 'power'), message (a plausible but fictional log message), severity (info/warn/error).
   Do not reference real MTA systems or real places. Save the result as a .jsonl file."

2. "Open scripts/load_search_index.py and show me where the corpus directory path is
   configured. Explain how to point it at a new subdirectory without breaking anything."

3. "In docs/extensions/02_swap_grounding_corpus/tests/test_corpus.py there are failing tests.
   Read them and tell me exactly what I need to create in data/mock_logs/ to make them pass."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/02_swap_grounding_corpus/tests/ -v
```

All tests **fail** until your new corpus and updated script are in place.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [01 — Add Health Analyst](../01_add_health_analyst/README.md) · Next: [03 — Add Tool](../03_add_tool/README.md)

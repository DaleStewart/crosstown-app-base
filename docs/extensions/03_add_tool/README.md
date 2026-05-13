# Extension 03 — Add a Tool to the Log Analyst

**Time:** ~30 min · **Use cases:** #1 (log analyzer), #2 (SCADA), #3 (DB health) · **Difficulty:** Easy

## What

The skeleton's Log Analyst ships with three tools: `search_logs`, `detect_pattern`, and
`summarize_incident`. This extension has your team add a **fourth tool**:
`correlate_lines(line_a, line_b, window_min)` — which looks for log events on two different
fictional rail lines that occurred within `window_min` minutes of each other, suggesting a
correlated fault. The orchestrator's tool registry is updated automatically when the tool is
registered correctly.

## Why

Use cases #1, #2, and #3 all benefit from cross-line correlation: a signal failure on L2 that
co-occurs with a SCADA timeout on L1 is a different kind of incident than one that does not.
Adding a fourth tool demonstrates how the agent framework grows incrementally — a key skill for
Track 2 teams.

## Try this

1. **Open the tools file.**
   The Log Analyst's tools live in `apps/log_analyst/tools.py` (or a similarly-named file —
   confirm with `ls apps/log_analyst/`).
2. **Add the new tool function.**
   The function signature must be:
   ```python
   def correlate_lines(line_a: str, line_b: str, window_min: int) -> dict:
       ...
   ```
   It must return a dict with at least these keys: `correlated_events` (list), `citations` (list).
3. **Register the tool with the agent.**
   Find where `search_logs`, `detect_pattern`, and `summarize_incident` are registered
   (look in `apps/log_analyst/main.py` or a `registry.py`) and add `correlate_lines` in
   the same way.
4. **Verify registration.**
   ```bash
   python -c "from apps.log_analyst import tools; print(dir(tools))"
   ```
   You should see `correlate_lines` in the output.
5. **Send a test query.**
   With the log analyst running, POST to `/tools/correlate_lines` with
   `{"line_a": "L1", "line_b": "L2", "window_min": 5}` and confirm a 200 response with
   a `citations` key.

## Prompt Copilot like this

```
1. "Open apps/log_analyst/tools.py. Following the exact same pattern used by search_logs,
   add a new function called correlate_lines(line_a: str, line_b: str, window_min: int) -> dict.
   It should search data/mock_logs/ for entries on line_a and line_b whose timestamps are
   within window_min minutes of each other and return
   {correlated_events: [...], citations: [...]}. Use only the stdlib — no new packages."

2. "Now open the file in apps/log_analyst/ that registers tools with the FastAPI app
   (likely main.py or registry.py). Show me where the three existing tools are registered
   and add correlate_lines in the same way."

3. "Write a one-liner pytest assertion that verifies correlate_lines is present in
   apps.log_analyst.tools and is callable."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/03_add_tool/tests/ -v
```

All tests **fail** until `correlate_lines` is implemented and registered.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [02 — Swap Grounding Corpus](../02_swap_grounding_corpus/README.md) · Next: [04 — Legacy Modernization](../04_legacy_modernization/README.md)

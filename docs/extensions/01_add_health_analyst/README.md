# Extension 01 — Add Health Analyst Agent

**Time:** ~60 min · **Use cases:** #2 (SCADA health), #3 (DB health reports) · **Difficulty:** Medium

## What

This extension adds a brand-new FastAPI microservice at `apps/health_analyst/` that acts as a second
specialist agent alongside the existing Log Analyst. It exposes three tools —
`pull_health_report`, `find_hidden_issues`, and `open_ticket` — and the orchestrator is updated to
route "health"-flavoured queries to it instead of (or in addition to) the Log Analyst.

## Why

The Log Analyst was built to mine text logs. Use cases #2 and #3 require reasoning over structured
health data (SCADA bridge telemetry for fictional lines L1/L2/L3, and periodic DB health reports).
Splitting responsibilities keeps each specialist small and testable, and demonstrates the
multi-agent routing pattern that is central to Track 2 of this hackathon.

## Try this

1. **Copy the Log Analyst as a starting point.**
   ```
   cp -r apps/log_analyst apps/health_analyst
   ```
2. **Replace the three tools.**
   Open `apps/health_analyst/tools.py` (rename if needed) and replace `search_logs`,
   `detect_pattern`, and `summarize_incident` with:
   - `pull_health_report(system_id: str)` — returns the latest health snapshot for a fictional
     system (e.g., `"L2-SCADA-bridge"`).
   - `find_hidden_issues(report_id: str)` — scans a report for anomalies not surfaced in the
     executive summary.
   - `open_ticket(issue_id: str, severity: str)` — records the issue in the mock ticketing store
     and returns a ticket number.
3. **Update the orchestrator routing prompt.**
   Open `apps/orchestrator/prompts/routing.txt` (or equivalent) and add a rule: if the user query
   mentions `health`, `SCADA`, `bridge`, or `ticket`, route to `health_analyst`.
4. **Smoke-test end-to-end.**
   Start both services and the orchestrator, then send the query
   _"What's wrong with the L2 SCADA bridge today?"_ — you should see the orchestrator call
   `health_analyst` and receive a response with a `citations` key.

## Prompt Copilot like this

```
1. "Using apps/log_analyst/main.py as the exact reference, create a sibling service
   apps/health_analyst/main.py that is a FastAPI app exposing these three tools as POST
   endpoints under /tools/:
     - pull_health_report(system_id: str) -> dict with keys: report_id, system_id, status, citations
     - find_hidden_issues(report_id: str) -> dict with keys: issues (list), citations
     - open_ticket(issue_id: str, severity: str) -> dict with keys: ticket_number, status, citations
   Keep the same response envelope shape used in log_analyst."

2. "In apps/orchestrator/agent.py (or the file that builds the routing prompt), add a routing
   rule that directs queries containing the words health, SCADA, bridge, or ticket to the
   health_analyst service. Show me only the diff."

3. "Write a pytest test in docs/extensions/01_add_health_analyst/tests/test_health_analyst.py
   that sends a POST to /tools/pull_health_report with body {\"system_id\": \"L2-SCADA-bridge\"}
   and asserts the response contains a citations key. Use httpx.AsyncClient and
   pytest-asyncio. The test should import from apps.health_analyst.main."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/01_add_health_analyst/tests/ -v
```

All tests **fail** until you complete the extension (the `apps/health_analyst` package does not
exist yet).

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: _(first extension)_ · Next: [02 — Swap Grounding Corpus](../02_swap_grounding_corpus/README.md)

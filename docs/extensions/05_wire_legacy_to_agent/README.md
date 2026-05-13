# Extension 05 — Wire Legacy Service to the Agent

**Time:** ~30 min · **Use cases:** #4 (data warehouse), #5 (PCICS) · **Difficulty:** Easy

## What

Extension 04 produced a standalone FastAPI service (`apps/legacy_service/`). This extension
**registers it as a callable tool** on the Log Analyst (or a new specialist agent), so the
orchestrator can invoke it when answering queries about incidents. The tool is named
`query_incidents` and it calls `GET /incidents` (or `GET /incidents/{id}`) on the legacy
service via an internal HTTP call.

## Why

Use cases #4 and #5 require the AI agent to answer questions that draw on data held in the
modernized legacy service (the fictional PCICS incident registry). Wiring it as a tool — rather
than making the orchestrator call it directly — keeps the agent framework consistent and makes
the tool independently testable.

## Try this

1. **Create the tool function.**
   Add `query_incidents(incident_id: int | None = None)` to
   `apps/log_analyst/tools.py` (or your chosen specialist's tools file). It should use
   `httpx.get` to call the legacy service (URL from an env var `LEGACY_SERVICE_URL`,
   default `http://localhost:8003`).
2. **Register the tool** in the same way as the other three tools (see Extension 03 for the
   pattern).
3. **Update the orchestrator routing prompt** to include a hint:
   _"If the user asks about incident IDs or the incident registry, use the query_incidents tool."_
4. **Smoke-test the chain.**
   With both services running, send the query
   _"What is the status of incident 1?"_ to the orchestrator and confirm it calls
   `query_incidents`.

## Prompt Copilot like this

```
1. "In apps/log_analyst/tools.py, add a function called query_incidents(incident_id=None).
   It should call the legacy service at the URL stored in env var LEGACY_SERVICE_URL
   (default http://localhost:8003). If incident_id is provided, call GET /incidents/{id};
   otherwise call GET /incidents. Return {incidents: <list>, citations: [LEGACY_SERVICE_URL]}."

2. "Register query_incidents in apps/log_analyst/main.py in the same way that search_logs
   is registered. Show me just the lines I need to add."

3. "Update the routing prompt in apps/orchestrator/ to route 'incident status' and
   'incident registry' queries to the tool query_incidents. Show me the exact text change."
```

## Acceptance

See [`acceptance.md`](./acceptance.md).

## Tests

Run:

```bash
pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v
```

All tests **fail** until `query_incidents` is added and registered.

## Links back

- [Use case map](../../use-case-map.md)
- [Architecture](../../architecture.md)
- Previous: [04 — Legacy Modernization](../04_legacy_modernization/README.md) · Next: [06 — Enable Modernize PR](../06_enable_modernize_pr/README.md)

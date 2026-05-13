# Acceptance — Extension 05

You're done when **ALL** of the following are true.

- [ ] `apps/log_analyst/tools.py` (or equivalent specialist tools file) contains a callable `query_incidents`.
- [ ] `query_incidents()` (no id) returns a dict with an `incidents` list and a `citations` list.
- [ ] `query_incidents(incident_id=1)` returns a dict with a single-item `incidents` list.
- [ ] The tool is registered so that `POST /tools/query_incidents` on the log analyst returns HTTP 200.
- [ ] The orchestrator's routing logic / prompt references `query_incidents` for incident-related queries.
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Start the legacy service: `uvicorn apps.legacy_service.main:app --port 8003`
2. Start the log analyst: `uvicorn apps.log_analyst.main:app --port 8002`
3. Start the orchestrator: `uvicorn apps.orchestrator.main:app --port 8000`
4. Run:
   ```bash
   curl -s -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the status of incident 2?"}' | jq .
   ```
   Show the coach that `query_incidents` appears in the tool-call trace and the response
   references the incident from the legacy service.
5. Run `pytest docs/extensions/05_wire_legacy_to_agent/tests/ -v` and show all green.

# Acceptance — Extension 01

You're done when **ALL** of the following are true.

- [ ] `apps/health_analyst/main.py` exists and defines a FastAPI app.
- [ ] `GET /health` on the health analyst service returns HTTP 200.
- [ ] `POST /tools/pull_health_report` with body `{"system_id": "L2-SCADA-bridge"}` returns HTTP 200 with a JSON body that includes a `citations` key.
- [ ] `POST /tools/find_hidden_issues` with a valid `report_id` returns HTTP 200 with a JSON body that includes an `issues` list.
- [ ] `POST /tools/open_ticket` with valid `issue_id` and `severity` returns HTTP 200 with a `ticket_number` key.
- [ ] The orchestrator routes the query _"What's wrong with the L2 SCADA bridge?"_ to `health_analyst` (visible in orchestrator logs or a unit test of the routing prompt).
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. In one terminal: `uvicorn apps.health_analyst.main:app --port 8001`
2. In another terminal: `uvicorn apps.orchestrator.main:app --port 8000`
3. Run:
   ```bash
   curl -s -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is wrong with the L2 SCADA bridge today?"}' | jq .
   ```
4. Show the coach that the response references `health_analyst` in the `agent` field and that the answer body contains fictional health data for line L2.
5. Run `pytest docs/extensions/01_add_health_analyst/tests/ -v` and show all green.

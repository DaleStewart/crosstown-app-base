# Acceptance — Extension 04

You're done when **ALL** of the following are true.

- [ ] `legacy/SampleController.cs` exists in the repository (the team pasted the snippet).
- [ ] `apps/legacy_service/main.py` exists and defines a FastAPI app.
- [ ] `GET /health` returns HTTP 200 with `{"status": "ok"}`.
- [ ] `GET /incidents` returns HTTP 200 with a JSON list; each item has `id`, `line`, `description`, `status`.
- [ ] `GET /incidents/1` returns HTTP 200 with a single incident object.
- [ ] `GET /incidents/0` (invalid id) returns HTTP 400.
- [ ] `POST /incidents` with a valid body `{"line": "L1", "description": "Test fault"}` returns HTTP 201.
- [ ] `POST /incidents` with an empty body returns HTTP 422 (Pydantic validation) or HTTP 400.
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Start the service: `uvicorn apps.legacy_service.main:app --port 8003`
2. Run each curl in sequence:
   ```bash
   curl -s http://localhost:8003/health | jq .
   curl -s http://localhost:8003/incidents | jq .
   curl -s http://localhost:8003/incidents/1 | jq .
   curl -s -X POST http://localhost:8003/incidents \
     -H "Content-Type: application/json" \
     -d '{"line": "L3", "description": "Power fluctuation sector 2"}' | jq .
   ```
3. Show `legacy/SampleController.cs` side-by-side with `apps/legacy_service/main.py` in the
   editor and point out the structural similarity (controller → router, action → endpoint).
4. Run `pytest docs/extensions/04_legacy_modernization/tests/ -v` and show all green.


## 🏗️ Acceptance criteria

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Edge cases listed | [██████████] 100% |
| Pass/fail thresholds | [██████████] 100% |
| Reviewer assigned | Stark (Architect) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Stark (Architect) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When acceptance criteria are revisited or team completes extension |

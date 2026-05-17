# Acceptance — Extension 03

You're done when **ALL** of the following are true.

- [ ] `apps/log_analyst/tools.py` (or equivalent) contains a callable named `correlate_lines`.
- [ ] `correlate_lines` accepts `(line_a: str, line_b: str, window_min: int)` and returns a dict.
- [ ] The returned dict contains at least the keys `correlated_events` (list) and `citations` (list).
- [ ] `POST /tools/correlate_lines` with body `{"line_a": "L1", "line_b": "L2", "window_min": 5}` returns HTTP 200.
- [ ] The orchestrator's tool registry lists `correlate_lines` alongside the three original tools (visible in `/tools` or equivalent discovery endpoint, or in registry source).
- [ ] All tests in `tests/` pass.
- [ ] Demoable in <5 min to a coach.

## Demo script

1. Start the log analyst: `uvicorn apps.log_analyst.main:app --port 8002`
2. Run:
   ```bash
   curl -s -X POST http://localhost:8002/tools/correlate_lines \
     -H "Content-Type: application/json" \
     -d '{"line_a": "L1", "line_b": "L2", "window_min": 5}' | jq .
   ```
   Show the `correlated_events` and `citations` keys in the response.
3. Run `pytest docs/extensions/03_add_tool/tests/ -v` and show all green.


## 🛠️ Acceptance criteria

| Metric | Status |
|--------|--------|
| Acceptance criteria | [██████████] 100% |
| Edge cases listed | [██████████] 100% |
| Pass/fail thresholds | [██████████] 100% |
| Reviewer assigned | Banner (Tester) |

| Field | Value |
|-------|-------|
| Last reviewed | 2026-05-17 |
| Reviewed by | T'Challa (Lead) |
| Doc owner | Banner (Tester) |
| Related PRs (recent) | (none in last 7 days) |
| Related branches in-flight | (none — exercise only) |
| Next review trigger | When acceptance criteria are revisited or team completes extension |

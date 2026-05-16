# Bug #12 diagnosis — 2026-05-15 (Banner)

## TL;DR — **NO BUG.** System is fully healthy. 422s were caused by a malformed test payload (`{"message": ...}` instead of `{"text": ...}`). All 3 tool paths produce real citations live, no warnings.

---

## Symptom reported
Sean reported `POST /api/turn` returning HTTP 422 during UAT after Okoye-2 deployed the real log-analyst image (Bug #11). Brief also noted `400 Bad Request` lines in log-analyst tail.

## Forensic trace

### What orchestrator's /api/turn expects
`apps/orchestrator/main.py:62-63`:
```python
class TurnRequest(BaseModel):
    text: str
```

Pinned by 11 existing pytest cases (`tests/test_api_turn.py`), the orchestrator eval runner, and the redteam runner — all use `text`.

### What the 422 actually said
```json
{
  "detail": [{
    "type": "missing",
    "loc": ["body", "text"],
    "msg": "Field required",
    "input": {"message": "Show me door-fault logs from Atlantic station"}
  }]
}
```

The bug brief's test command sent `{"message": ...}` — the orchestrator correctly rejected it as malformed. **Pydantic was doing its job.** This is not a contract drift; this is a misformed client payload.

### Re-test with canonical `{"text": ...}` — all green

```
=== search_logs ===
citations: 10  warnings: NONE
tool_calls: [{"name":"search_logs","arguments":{"query":"door fault Atlantic station"}}]

=== detect_pattern ===
citations: 39  warnings: NONE
tool_calls: [{"name":"detect_pattern","arguments":{"log_id":"L-001234"}}]

=== summarize_incident ===
citations: 2  warnings: NONE
tool_calls: [{"name":"summarize_incident","arguments":{"incident_id":"INC-1001"}}]
```

Numbers match Banner's earlier Bug #10 smoke exactly (10 / 39 / 2). detect_pattern still resolves `{"log_id": "L-001234"}` ← Bug #10 fix in PR #16 holds.

### The "400 Bad Request" lines in log-analyst tail — explained
```
22:36:53  POST /tools/search_logs  400  ← model tried time_range as a STRING
22:36:56  POST /tools/search_logs  400  ← same
22:37:01  POST /tools/summarize_incident  200  ← model self-corrected
22:44:16+ everything 200
```
This is the **documented Bug #10 secondary symptom**: with the real schema visible to the Realtime model, it sometimes tries `time_range: "last 24 hours"` instead of `{from, to}`. The model self-corrects on retry within the same turn, so `/api/turn` returns 200 with citations. Banner's PR #16 history flagged this as "minor model wobble, not a blocker" and the live smoke confirms net-zero customer impact (warnings: NONE, citations: 10).

### The 422s in orchestrator tail
```
22:41:56  POST /api/turn  422  ← someone sent {"message":...}
22:43:47  POST /api/turn  422  ← someone sent {"message":...}
22:44:21+ all 200
```
Exactly two 422s, sandwiched between 200s. Consistent with a human (likely Sean or the brief's automated test) sending the wrong field, then retrying correctly.

## Mystery resolution — "How did earlier smoke get 39 citations if log-analyst was Hello World?"

**Answer: scenario (d).** Log-analyst was already on the real image during Banner's Bug #10 verification at ~22:18Z. Okoye-2's redeploy at 22:29Z (`log-analyst--azd-1778884163`) was likely a re-push of the same/newer real image, not a Hello-World → real transition.

Evidence:
- The `log-analyst--azd-1778884163` revision (created 22:29Z) is the **only active revision**, and `az containerapp revision list` only shows revisions for the current image lineage. Earlier real-image revisions may have been pruned.
- Banner's Bug #10 verification at 22:18:37–22:19:05 saw `/api/turn` 200 OK with 10/39/2 citations — those numbers cannot come from a Hello World image and cannot come from a Cosmos/Search local fallback (orchestrator has no such fallback — code path in `main.py:97-119` always goes through `tools.dispatch` → HTTP → log-analyst, and 400s would surface as warnings).
- Therefore log-analyst was serving real tool responses at 22:18Z, contradicting the brief's premise that it was Hello World until 22:29Z.

**No architectural concern.** There is no hidden fallback; orchestrator faithfully dispatches to log-analyst. Okoye-2's revision-history read was likely incomplete (ACA prunes old revisions; only the latest active one was visible at the time she checked).

## Fix details
**None shipped.** No code change is warranted:
- Orchestrator contract (`text: str`) is correct and pinned by 11 tests + eval runner + redteam runner.
- Log-analyst contract is correct (returning 200s for well-formed payloads, 400s only for model wobble that self-corrects).
- All 3 tool paths produce non-empty citations with no warnings on live `/api/turn`.

**Action for Sean:** Use `{"text": "..."}` in UAT requests (matches README, evals, redteam). Confirmed live-working examples copied to inbox D-027.

## Recommendation (out of scope, optional follow-up)
Consider tightening `search_logs.time_range` schema with an example value in the description so the Realtime model stops attempting the string form. Already tracked as a Bug #10 follow-up note; still not a blocker.

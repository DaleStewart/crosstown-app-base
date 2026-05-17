# Parker — Agent History (Active)

Peter Parker / Spider-Man — Frontend developer. MTA AI Hackathon.

---

**Note:** Detailed history moved to .history-archives/parker-history-2026-05-13-to-2026-05-15.md for archival. This file tracks current work.

---

## 2026-05-16 — T105 Phase 1 Batch Intake

**Task:** T105 (Medium) — Frontend Dockerfile HEALTHCHECK config (Phase 1 deploy-hygiene batch).

**Status:** ✅ Complete. Branch: chore/deploy-hygiene.

**Deliverable:**
- **apps/frontend/Dockerfile:** curl-based HEALTHCHECK probes http://localhost:3000/api/health (proxied by nginx to orchestrator /health). Every 30s, 5s timeout, 20s start period, 3 retries. curl adds ~2–3 MB to production image (acceptable).

**Verification:** Static syntax check passing. Docker daemon deferred (Windows environment).

**Batch outcome:** Anvil PR #29 review — **PASS ✅**. Six high-value checks all pass. Frontend HEALTHCHECK couples locally to orchestrator (soft concern; ACA Bicep probes override).

**Decision:** D-030 (merged into D-028).

## 2026-05-16 — Smoke-test retry for ACA revision-flip window

**Task:** Add bounded retry loop to smoke check 2 (and check 3 shape audit) in `scripts/smoke-test.sh` and `scripts/smoke-test.ps1`.

**Status:** ✅ Complete. Committed to main.

**Deliverable:**
- Check 2 (`GET /api/health → service:orchestrator`) now retries with exponential backoff (5s → 10s → 15s cap) for up to `SMOKE_RETRY_SECONDS` (default 90s) before hard-failing with the original grader-compatible message.
- Check 3 (direct orchestrator /health) only asserts HTTP 200, not the service field — no revision-flip exposure, no retry needed.
- PowerShell parity: same envelope in `smoke-test.ps1`, same `$env:SMOKE_RETRY_SECONDS` override.

## Learnings

- **ACA revision flips take 1–30 s to route traffic to the new revision.** Smoke gates that run immediately after `azd deploy` returns can hit the old revision and see stale JSON (e.g., `service=""`). The fix is a deadline-based retry loop (not a fixed sleep) so fast deploys stay fast and slow flips don't false-fail.
- Smoke check 4 needed same retry envelope as check 2 — first /api/turn after cold start is LLM-bound, ~14s.



2026-05-16 — In push-to-talk WS protocols, the `stop` frame is the commit boundary — without it the server has no idea the user finished talking. Always verify both sides of the conversation boundary (start + stop) are wired at the same call site, not split across different functions with different call semantics.

## 2026-05-16 — Text input for typed questions (PR #23) (Parker)

Sean requested a text input alongside push-to-talk so users can type questions when voice is unavailable (or just prefer typing).

**Autopilot disclosure:** acted in autopilot for this task per the system prompt directive. Requestor: Sean (AFK during execution).

**Changes (4 files):**
- `apps/frontend/src/components/TextInput.tsx` — new controlled-input component; POST /api/turn with {text} body; optimistic user bubble; appends assistant response; error turn on failure; disables + "Sending..." while in-flight
- `apps/frontend/src/hooks/useVoiceSession.ts` — two new reducer actions (append_user, append_assistant) + appendUserTurn(text) / appendAssistantTurn({text, citations, warnings}) exposed on UseVoiceSession; append_assistant pushes a synthetic ToolCallEntry when citations/warnings present (shows in side panel)
- `apps/frontend/src/App.tsx` — imports TextInput, destructures appendUserTurn/appendAssistantTurn from hook, renders TextInput below Transcript
- `apps/frontend/tests/useVoiceSession.test.ts` — 3 new tests: appendUserTurn without WS, appendAssistantTurn with citations (synthetic tool entry created), appendAssistantTurn with no citations (no tool entry)

**47doors pattern observed:** ChatInput.tsx uses a callback prop (onSend) — stateless component, no direct API knowledge. useChat.ts owns optimistic user message + API call + state append. Adapted: onUserTurn / onAssistantTurn prop callbacks; hook owns all state.

**Gates:** lint pass, typecheck pass, vitest 9/9 pass (+3 new; was 6), build pass (1525 modules, 179.81 kB)

**Deploy:** ACR run dtg -> text-input-1778951364; az containerapp update -> revision frontend--0000005 (Healthy, 100% traffic).

**D-034 filed.**
**PR #23:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/23

**Live verify:** Deferred to user UAT. Sean to open frontend, type "Show me door-fault logs from Atlantic station", hit Send -- expect user bubble immediately + assistant response with citations after API call returns.

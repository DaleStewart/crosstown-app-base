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
Sean reported UAT mic button dead. Diagnosed end-to-end and shipped PR #17.

**🤖 Autopilot disclosure:** acted in autopilot for this task per the system prompt directive. No human gates between diagnosis and shipping.

**Symptom:** Live UAT frontend rendered fine; clicking the mic button did nothing.

**Diagnostic path:**
1. Installed `@playwright/test` + chromium in `apps/frontend`, wrote `e2e/mic-button.spec.ts` to capture WS events, console errors, network failures against the live URL with `--use-fake-ui-for-media-stream` so `getUserMedia` doesn't gate the click.
2. Pre-fix run (`.squad/files/playwright-mic-button-2026-05-16.log`): click handler fires, browser opens `wss://frontend.../ws/voice`, gets **HTTP 502** on the WS upgrade.
3. Verified orchestrator is healthy: direct `websockets.connect` to `wss://orchestrator.blackriver-.../ws/voice` succeeds (`.squad/files/probe_ws.py`).
4. Frontend container nginx error logs (`az containerapp logs show --name frontend`): `peer closed connection in SSL handshake (104: Connection reset by peer) while SSL handshaking to upstream, upstream: "https://100.100.244.199:443/ws/voice", host: "frontend.blackriver-..."`.

**Root cause:** nginx's `proxy_pass https://...` to ACA was missing **SNI** (`proxy_ssl_server_name on;` + `proxy_ssl_name`) and was forwarding the wrong **Host header** (inbound `frontend.blackriver-...` instead of the orchestrator's hostname). ACA front door routes by SNI/Host and resets handshakes that lack them.

**Fix shipped (`squad/fix-frontend-mic-button` → PR #17, stacked on `squad/fix-log-analyst-detect-pattern-400`):**
- `apps/frontend/docker-entrypoint.sh` — derive `ORCHESTRATOR_HOST` from `ORCHESTRATOR_URL` (sed-strip scheme/path/port); export both for envsubst.
- `apps/frontend/nginx.conf` — on both `/api/` and `/ws/`: add `proxy_set_header Host $ORCHESTRATOR_HOST;`, `proxy_ssl_server_name on;`, `proxy_ssl_name $ORCHESTRATOR_HOST;`. Existing WS `Upgrade`/`Connection` headers preserved.
- Did **not** touch any React/TS code. `useVoiceSession`'s same-origin `wss://` URL construction is correct by design — the nginx hop is the intended data path. Frontend was innocent.

**Build/lint/test (local):** lint ✅, typecheck ✅, build ✅ (1524 modules / 177.28 kB JS — bundle unchanged, config-only fix).

**Deploy:** `azd deploy frontend` aborted with "Docker service not running" on the operator box. Fell back to Okoye's ACR-push fallback per Day-5 ops pattern:
- `az acr build --registry crcrosstowndryrunmay15yycemmso7sk7q --image mta-ai-hackathon/frontend-crosstown-dryrun-may15:mic-fix-20260516094226 -f Dockerfile .` (build ran in ACR; CLI log streaming threw a Windows `cp1252` encoding error on the build's check-mark glyph but the build itself completed — image confirmed via `az acr repository show-tags`).
- `az containerapp update --name frontend --image ...mic-fix-20260516094226` rolled revision `frontend--0000002` to 100% traffic, `healthState: Healthy`.

**Post-deploy verification (Playwright re-run, `.squad/files/playwright-mic-button-postfix-2026-05-16.log`):**
- `[opened] wss://frontend.../ws/voice` — no more 502
- `[sent] {"type":"start","conversationId":null,"mode":"push_to_talk"}` — start frame went out
- 14 follow-on binary PCM frames sent (fake media stream audio)
- **0 WS errors, 0 closes, 0 network failures** in the 7 s observation window
- Lingering cosmetic `404` on `/api/health` (orchestrator only serves `/health`, not `/api/health`) — pre-existing, unrelated.

**Verdict:** Sean can UAT the push-to-talk button — it now opens a real WebSocket session to the orchestrator. Full voice loop (audio response back from Foundry Realtime) still depends on Bug #8 (orchestrator-side WS handshake 404), which remains with Brady; that's independent of this fix.

**Followups:**
- The `/api/health` 404 on every page load — frontend should either probe `/api/health` (and orchestrator add a route) or use `/health` directly. Cosmetic but visible in console. Not in scope for this P0.
- Playwright `test:e2e` script added but **not** wired into default CI — it points at the live UAT URL by design (diagnostic). If we want it in CI it should target a hermetic dev server.

## 2026-05-16 — Missing stop frame bug fixed (PR #19) (Parker)

Sean reported hold-mic → button turns yellow → release → chat empty. Diagnosed and shipped.

**🤖 Autopilot disclosure:** acted in autopilot for this task per the system prompt directive. Requestor: Sean (not Brady).

**Diagnostic path:**
1. Read `useVoiceSession.ts` and immediately spotted: `stopTalking()` never calls `send({ type: "stop" })`. The stop frame only appears in `disconnect()` (full session teardown), not on every mic release.
2. Created `e2e/mic-hold-release.spec.ts` — simulates 2 s hold + release, captures all WS frames.
3. Pre-fix Playwright run: 16 frames sent (1 start + 15 binary PCM), **0 received**, no stop frame. Chat DOM unchanged: "No transcript yet. Hold to talk."
4. Post-fix Playwright run (against deployed revision): 17 frames sent — stop frame `{"type":"stop"}` now present immediately after PCM block.

**Root cause:** `stopTalking()` in `useVoiceSession.ts` stopped the mic and set `recording: false` but never signaled the orchestrator. The orchestrator waits for `{type:"stop"}` to commit the audio buffer and generate a response.

**Fix (2 files):**
- `stopTalking()` now calls `send({ type: "stop" })` after `mic.stop()`. Added `send` to dep array.
- `disconnect()` removes its own duplicate stop send (now done via `stopTalking()`). Removed `send` dep.

**Validation:** lint ✅, typecheck ✅, build ✅ (1524 modules / 177.26 kB JS — bundle unchanged).

**Deploy:** ACR build `mic-stopframe-fix-20260516101747` → `frontend--0000003` (Healthy, 100% traffic).

**D-030 filed.** PR #19: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/19

**Residual (Wanda's scope):** WS RECEIVED still 0 after fix — orchestrator needs to handle the stop frame and return `transcript_delta`/`final` events for the full loop to close.

## Learnings

2026-05-16 — nginx → ACA HTTPS upstream **always** needs `proxy_ssl_server_name on;` + `proxy_ssl_name $host;` + `proxy_set_header Host $host;`. The default behavior (no SNI, inbound Host forwarded) silently produces 502s with the diagnostic `peer closed connection in SSL handshake` line in error logs. Worth baking into any future ACA-fronted nginx template.

2026-05-16 — In push-to-talk WS protocols, the `stop` frame is the commit boundary — without it the server has no idea the user finished talking. Always verify both sides of the conversation boundary (start + stop) are wired at the same call site, not split across different functions with different call semantics.

## 2026-05-16 — User-turn transcripts in chat (PR #21) (Parker)

Sean reported the chat only showed assistant responses — not a real conversation. Wanda (in parallel) is re-enabling `input_audio_transcription` on the orchestrator and will forward `user_transcript` events. This PR wires up the frontend to receive and render those events.

**🤖 Autopilot disclosure:** acted in autopilot for this task per the system prompt directive. Requestor: Sean.

**Changes (4 files):**
- `apps/frontend/src/lib/protocol.ts` — `UserTranscript` type added; `parseServerMessage` normalizes all 4 Wanda event-name aliases to `{ type: "user_transcript", text, item_id? }`. Aliases handled: `user_transcript`, `user_transcript_completed`, `input_audio_transcription_completed`, `transcript_user_final`.
- `apps/frontend/src/hooks/useVoiceSession.ts` — `applyFrame` case for `user_transcript` appends `{ role: "user", final: true }` to `transcripts`. Empty-text no-op.
- `apps/frontend/tests/useVoiceSession.test.ts` — 2 new tests: canonical event and all 4 alias names.
- `apps/frontend/tests/protocol.test.ts` — alias normalization test + `UserTranscript` recognized by `isServerMessage`.

**`Transcript.tsx`:** No change needed — `role: "user"` was already styled as right-aligned blue bubble (`bg-subway-blue text-white self-end`).

**Gates:** lint ✅, typecheck ✅, vitest 9/9 ✅ (was 6; +3 new), build ✅ (177.79 kB).

**Deploy:** ACR build run `dta` → `user-transcript-20260516111507`; `az containerapp update` → revision `frontend--0000004` (Healthy, 100% traffic).

**Live verify:** Waiting on Wanda's server-side deploy. Once both are live: hold mic → release → confirm user bubble (blue, right) + assistant bubble (grey, left) appear in chat.

**D-032 filed.**
**PR #21:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/21


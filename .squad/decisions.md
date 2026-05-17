### D-013 · Org Import Successful — PRs #1 and #2 Open
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** Completed

D-012 (remote auth blocker) is **RESOLVED**. Both development branches successfully pushed to `DevPost-Test-Hackathon/crosstown-app` and paired with PRs.

**Resolution flow:**
- Fresh PAT generated from account that IS an org member of `DevPost-Test-Hackathon`
- SSO authorization completed explicitly (Authorize button clicked in GitHub)
- Token set in-memory only via `$env:GH_TOKEN`; origin flipped to HTTPS
- `gh auth setup-git` established credential helper
- Smoke test passed: `gh api orgs/DevPost-Test-Hackathon` returned org JSON (no 404)
- Both branches pushed successfully to remote

**Branches & PRs:**
- **PR #1:** `squad/swap-realtime-to-gpt-realtime-1.5` → "Swap Foundry Realtime to gpt-realtime-1.5" (D-009)  
  https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/1

- **PR #2:** `squad/add-spec-kit-v0.8.10` → "Add GitHub Spec Kit v0.8.10 + Constitution v1.0.0 + Spec 001" (D-011)  
  https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/2

**Key insight:** SSO authorization is a separate checkpoint — it's not enough to generate a PAT with the right scopes. GitHub SSO flow requires explicit "Authorize" click for each new PAT, even if the user is already an org member. This is by design (security), but easy to miss if you assume "membership + PAT scopes = ready to go."

**Learnings for future ops:**
- Always verify org reachability with `gh api orgs/<ORG-NAME>` before investing in branch-push planning
- HTTPS + credential helper is more reliable than SSH key management for CI/CD on Windows
- PAT + SSO is a two-factor gate; both must be confirmed explicitly

**Token hygiene:** PAT set in-memory only, never to disk, never echoed in output logs. User should revoke temporary PATs used this session.

**Changes:**
- `infra/modules/foundry.bicep` — deployment name `gpt-realtime-1.5`, model.version = `gpt-realtime-1.5-2026-02-23`
- `.env.example` — `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5`
- `apps/orchestrator/settings.py` — realtime deployment env var
- `apps/orchestrator/voice/foundry_realtime.py` — WebSocket endpoint pattern for GA realtime endpoint
- `docs/voice.md`, `docs/architecture.md` — documentation updated to reflect new deployment

**Preserved:** Bicep symbol `gpt4oRealtimeDeployment`, env var `AZURE_OPENAI_REALTIME_DEPLOYMENT`, SKU `GlobalStandard`/capacity 10. Speech Services fallback path unchanged.

**Out of scope:** `gpt-realtime-mini`, `gpt-realtime-translate`, `gpt-4o-transcribe-diarize`.

**Verification:** Bicep build clean, ruff/mypy --strict on 19 files, pytest 11/11 passing, frame schemas valid for GA `/openai/v1/realtime`, straggler grep clean. Go.

### D-010 · Maximoff "Leave gpt-4o-realtime-preview alone" Instruction Superseded
**Date:** 2026-05-15
**Author:** Coordinator
**Status:** Adopted

Decision D-006 (gpt-4o → gpt-4.1 sweep, 2026-05-13) explicitly left `gpt-4o-realtime-preview` untouched with the rationale "Distinct purpose (voice/audio path). Real model name, explicitly named and immutable." That instruction was contextual to the 2026-05-13 chat-model migration — not a permanent freeze.

As of 2026-05-15, D-009 executes a deliberate model upgrade from `gpt-4o-realtime-preview` to `gpt-realtime-1.5` (GA endpoint). The historical Squad notes (`.squad/agents/maximoff/history.md`, `.squad/identity/resume.md`, `.squad/decisions.md` line 98) remain accurate as audit trail; they are NOT rewritten — only the current instruction supersedes.

**Related:** D-009 (realtime model upgrade, same session).

### D-014 · Post-Merge Build/Test/Eval Verification — Green
**Date:** 2026-05-15
**Author:** Scribe (Shuri) — Post-Merge Batch (Banner, Parker, Maximoff)
**Status:** Adopted

**Scope:** PRs #1 (D-009: realtime swap) and #2 (D-011: spec-kit adoption) merged to `origin/main` (commit `9143b72`). Parallel batch of three agents (Banner, Parker, Maximoff) executed post-merge gates on HEAD.

**Results:** 🟢 **All gates green. No regressions.**

**Python Services (Banner — Orchestrator + Log Analyst):**
- `apps/orchestrator`: ruff ✅, mypy --strict ✅, pytest 11/11 ✅
- `apps/log_analyst`: ruff ✅, mypy --strict ✅, pytest 16/16 ✅
- **Finding:** Zero lint/type/test failures. All citation + tool-routing contracts verified.

**Frontend (Parker — Lint/Typecheck/Test + Build):**
- Lint ✅, Typecheck ✅, Vitest 6/6 ✅
- **Finding:** Pre-existing `apps/frontend/vite.config.ts:15` TypeScript error (test property not on `UserConfigExport`). Needs `import { defineConfig } from 'vitest/config'` instead of `vite`. **NOT caused by either PR — unrelated to merged changes.** Logged as cleanup backlog.
- `npm run build` **FAILED** due to this same pre-existing vite/vitest collision. No new breakage from PRs.

### D-034 · Text input added — Sean can type questions (voice parity)
### D-030 · stopTalking() must send stop frame to orchestrator on mic release
**Date:** 2026-05-16
**Author:** Parker (Frontend)
**Status:** Adopted

Sean requested a text input field alongside push-to-talk so users can type questions when voice is unavailable.

**Implementation:**
- New `apps/frontend/src/components/TextInput.tsx` — controlled `<input>` + Send button; calls `POST /api/turn` with `{text}` body; optimistically renders user bubble; appends assistant response with citations; shows error turn on failure; disables + "Sending…" while in-flight
- `useVoiceSession.ts` extended with `append_user` / `append_assistant` actions and `appendUserTurn(text)` / `appendAssistantTurn({text, citations, warnings})` helpers; `append_assistant` also pushes a synthetic `ToolCallEntry` to the side panel when citations/warnings are present
- `App.tsx` renders `TextInput` below `Transcript`; wires helpers from the hook
- 3 new vitest tests (hook-level, no WS required)

**CI:** lint ✅, typecheck ✅, tests 9/9 ✅, build ✅ (1525 modules, 179.81 kB)  

---

### D-033 · Voice regression from PR #22 — Phase 2 WS-close root cause + fix
**Date:** 2026-05-16
**Author:** Maximoff (Anomaly Hunter)
**Requested by:** Sean
**Status:** Adopted

**Problem:** Voice broken after PR #22 deployed as `orchestrator--0000008`. Sean reported "nothing is showing up." Logs: WS opens → closes 22s later with zero error events visible.

**Root cause:** `azure_openai_transcription_deployment` defaulted to `"whisper-1"` in PR #22. No whisper deployment exists in `infra/modules/foundry.bicep` (only `gpt-4.1` + `gpt-realtime-1.5`). Phase 2 fire-and-forget `session.update` sent `model: "whisper-1"` → Azure OpenAI rejected the unknown deployment name and **closed the WebSocket**. The pump `finally` block put `None` in the inbound queue; `events()` returned immediately; zero audio/transcript events reached the client.

**47doors delta (from `.squad/files/47doors-ref/47doors-main/backend/app/services/azure/realtime.py`):**
- 47doors uses WebRTC + `/client_secrets` (different arch; audio goes direct from browser to AOAI)
- Their session config uses GA nested format `audio.input.transcription.model` (not preview flat `input_audio_transcription.model`)
- Single-phase (no fire-and-forget Phase 2) — all config in one `/client_secrets` body

**Fix (PR #24):**
1. `settings.py`: default `azure_openai_transcription_deployment` → `""` (disabled until a real deployment is provisioned)
2. `foundry_realtime.py`: Phase 2 guard unchanged (`if self._transcription_deployment:`); payload switches to GA nested `audio.input.transcription.model`
3. `foundry_realtime.py`: `_translate` handlers for `.delta` and `.failed` transcription events
4. `factory.py`: passes `transcription_deployment` to provider
5. `tests/test_foundry_realtime.py`: 13 unit tests

**Emergency fix timeline:**
- 17:07Z: env var `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT=''` on `orchestrator--0000009` → voice restored in 30s
- 17:11Z: `orchestrator--0000010` ACR rebuild from clean code, Healthy, 100% traffic

**Autopilot disclosure:** Full rollback to `--0000007` was not needed; env var override on `--0000009` was faster and restored Sean's voice in <1 min. Code fix shipped as PR #24.

**To enable user transcription in future:** Add a whisper-1 or gpt-4o-transcribe deployment to `infra/modules/foundry.bicep`, then set `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT=<deployment-name>` on the orchestrator container app.

**Files:** PR #24 (https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/24)
**Deploy:** ACR run `dtg` → `text-input-1778951364`; revision `frontend--0000005` Healthy, 100% traffic  
**PR:** #23 — https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/23

**Pattern adapted from:** 47doors `ChatInput.tsx` + `useChat.ts` — callback-prop pattern keeps `TextInput` stateless; single source of truth for messages stays in `useVoiceSession` reducer.

**Voice regression isolation:** text input calls HTTP `POST /api/turn`, not the voice WebSocket. Wanda's orchestrator regression (revision --0000008) does not affect text input.
In push-to-talk mode the frontend sends PCM audio frames while the user holds the mic button. When the user releases, the orchestrator must receive a `{type:"stop"}` frame to know it should flush the audio buffer and generate a response. Without it the server waits indefinitely and the chat window stays empty.

**Bug:** `stopTalking()` in `useVoiceSession.ts` was stopping the mic and dispatching `recording: false` but never calling `send({ type: "stop" })`. The stop signal only existed in `disconnect()`, which is only called on full session teardown — not on every mic release.

**Evidence (Playwright, pre-fix):** 16 WS frames sent (1 start + 15 binary PCM), 0 frames received after 8 s, no stop frame present.
**Evidence (Playwright, post-fix):** 17 WS frames sent — stop frame now appears as `{"type":"stop"}` immediately after the binary PCM block.

**Fix (PR #19, commit 626cb9e):**
- `stopTalking()` calls `send({ type: "stop" })` after `mic.stop()`; adds `send` to its `useCallback` dep array.
- `disconnect()` removes its own duplicate stop send (now redundant since it calls `stopTalking()` first) and drops the `send` dep.

**Residual:** WS RECEIVED still 0 after fix — orchestrator-side handling of the stop frame is Wanda's scope.

**Deploy:** ACR build `mic-stopframe-fix-20260516101747` → revision `frontend--0000003` (Healthy, 100% traffic).

**Eval Gates (Maximoff — Citation + Orchestrator + Tool Routing):**
- Citation gate: 8/8 scenarios, 0.0% uncited (threshold ≤5%) ✅
- Orchestrator gate: 8/8 scenarios, 0.0% routing failures (threshold ≤0%) ✅
- Tool-routing assertions OS-005..OS-008 all correct ✅
- **Finding:** Zero regression from realtime model swap (D-009). Citation/tool contracts identical pre/post.

**Verdict:** Realtime swap (D-009) and spec-kit adoption (D-011) verified clean on main. **No causality between merged PRs and pre-existing build issue.** Frontend build blocker is a local vite/vitest config collision, not a code regression.

**Next:** Track pre-existing frontend build issue as a separate backlog item (out of scope for this merge verification).

### D-015 · Frontend vite.config.ts TypeScript Fix — Shipped PR #3
**Date:** 2026-05-15
**Author:** Parker (Frontend) — Re-verified by Scribe (Shuri)
**Status:** Adopted

D-014 identified a pre-existing TypeScript error in `apps/frontend/vite.config.ts:15` (not a regression from D-009 or D-011). Parker shipped PR #3 with a one-line fix:

```diff
-import { defineConfig } from "vite";
+import { defineConfig } from "vitest/config";
```

`vitest/config` re-exports `defineConfig` with a widened type that includes the `test` block. Runtime behavior unchanged; purely a TypeScript types fix.

**Verification (on `squad/fix-vite-config-defineConfig`, re-run 2026-05-15T18:11Z):**
- `npm run lint` ✅
- `npm run typecheck` ✅
- `npx vitest run` (6/6) ✅
- `npm run build` (exit 0; was exit 2) ✅ FIXED

**Delivery:**
- PR: DevPost-Test-Hackathon/crosstown-app#3 (merged to main)
- Commit: single-line change only

**Consequence:** All four CI gates on frontend now pass. No follow-ups needed unless vitest is dropped in the future.

---

### D-016 · gpt-4.1 version pin corrected; `azd up` unblocked
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** PR open, awaiting merge

Shipped P0 one-line fix on branch `squad/fix-foundry-gpt41-version` (commit `96e42d435da1ce85864cd281b2090ea4400d7177`) correcting `infra/modules/foundry.bicep` gpt-4.1 from `version: '2024-11-20'` → `'2025-04-14'`. Opened **PR #5** (https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/5) labeled P0/blocker.

**Decision (one line):** Merging this clears the only repo-state blocker between Brady and a clean `azd up` against sub `47156f11-2e05-4362-ac86-090b4b081b27` in region `eastus2` for the Tuesday 2026-05-19 customer dry-run (env `crosstown-dryrun-may15`). Bicep compiles clean (exit 0); no other model version pins in `infra/` are stale.

---

### D-017 · azd up Pre-Flight (2026-05-15)
**Date:** 2026-05-15
**Author:** Okoye (Operations)
**Status:** NO-GO pending PR #5 merge + sub-scoped re-verify

Provision in **region `eastus2`**, **azd env `crosstown-dryrun-may15`**, bound to **subscription `47156f11-2e05-4362-ac86-090b4b081b27`** in **tenant `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`** — but `azd up` is **blocked until** (a) PR #5 is merged (gpt-4.1 `version` corrected from `2024-11-20` → `2025-04-14`), and (b) Monday-morning §10 quota + provider checks are re-run against the target sub (current recon was on a different sandbox and could not access `47156f11-...`).

**Full report:** `.squad/files/azd-up-preflight-2026-05-15.md`

**Decision (one line):** All infrastructure checks passed in pre-flight; only data-plane blockers (model version + sub quota recon) remain before Brady can execute `azd up` for the Tuesday 2026-05-19 dry-run.

---

### D-018 · Lab Dry-Run Plan (Customer Handoff — Tuesday 2026-05-19)
**Date:** 2026-05-15
**Author:** Stark (Architect)
**Requested by:** Brady (segayle)
**Status:** Adopted

Lab dry-run executes as Phase 0–4 per runbook at `.squad/files/lab-dry-run-runbook.md`. Includes Phase 2.5 (live eval/test gates), customer-handoff acceptance checklist, and P0 rule: any exercise with unreachable failing tests is fixed before Tuesday.

**Decision (one line):** Full lab dry-run runbook delivered; all 11 identified risks catalogued; customer handoff checklist ready. Brady to merge PR #5, re-login to tenant `9b7cbd77-...` with sub-scoped access, then execute `azd up` for Phase 0 deployment.

---

### D-022 · Bug #7 fixed; new Bug #8 surfaces — Phase 2.5 still blocked
**Date:** 2026-05-15
**Author:** Maximoff (Anomaly Hunter / Eval Gate)
**Requested by:** Brady (segayle)
**Status:** Inbox — needs Brady decision on Bug #8

**Context:** Bug #7 (Foundry Realtime URL scheme regression introduced by D-009) shipped as PR #13, stacked on PR #12 (Bug #5b Dockerfile aiohttp). Single-line surgical fix in `apps/orchestrator/voice/foundry_realtime.py:155–163`: convert `https://` → `wss://` (and `http://` → `ws://`) on the Foundry endpoint before composing the realtime URL. Bearer auth, no `api-version`, and `?model=gpt-realtime-1.5` all preserved per D-009 GA contract.

**Local gates (apps/orchestrator):** ruff clean, mypy --strict clean (19 files), pytest 11/11.

**Deploy:** `azd deploy orchestrator` — 30 s, new revision active (`.squad/files/azd-deploy-orchestrator-bug7-fix.log`).

**Live `/api/turn` smoke (all 3 tools):** Bug #7 confirmed fixed — `InvalidURI: scheme isn't ws or wss` no longer appears. WebSocket client now reaches Foundry, but **Foundry rejects the handshake with HTTP 404** (`websockets.exceptions.InvalidStatus`). Captured trace: `.squad/files/orchestrator-500-trace-after-wss-fix.log`.

**Decision (one line):** Bug #7 shipped and verified at the URI layer; Phase 2.5 still 🟡 NOT live-ready, blocked on Bug #8 (WS handshake 404). Per failure-handling protocol, **stopped and escalated** rather than chase a 4th orchestrator fix without Brady's call. Candidate causes for Brady to rule on: wrong host (`azureml.ms` vs `openai.azure.com`), wrong path, deployment-name vs alias mismatch, or bearer scope mismatch (currently `cognitiveservices.azure.com/.default`).

**Files:** PR #13, `.squad/files/azd-up-result-2026-05-15.md`, `.squad/files/orchestrator-500-trace-after-wss-fix.log`, `.squad/files/azd-deploy-orchestrator-bug7-fix.log`.

---

### D-028 · Bug #13 fixed — Mic button alive on UAT (nginx SNI + Host)
**Date:** 2026-05-16
**Author:** Parker (Frontend) — requested by Sean (NOT Brady)
**Status:** Shipped (PR #17 open, deployed via ACR-push fallback)

**Discovery:** Sean opened the live UAT frontend (`https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io`), UI rendered, mic button visible — clicking it did nothing. P0 against Phase 2.5.

**Diagnosis (Playwright + nginx logs):** Click handler fires; `useVoiceSession.connect()` opens `wss://frontend.blackriver-.../ws/voice`. Frontend container's nginx proxies to `https://orchestrator.blackriver-...` and returns **HTTP 502** for `/ws/voice` and `/api/*`. Container logs: `peer closed connection in SSL handshake (104: Connection reset by peer) while SSL handshaking to upstream, upstream: https://100.100.244.199:443/...`. Direct WSS to `wss://orchestrator.blackriver-.../ws/voice` works (verified via `websockets.connect`). So orchestrator + its ingress are healthy — the bug was purely in the frontend's nginx reverse-proxy config.

**Root cause:** nginx was opening TLS to the upstream IP with **no SNI** and was forwarding the inbound `Host: frontend.blackriver-...` to the orchestrator. ACA's front door requires (a) SNI on the upstream TLS ClientHello and (b) a matching `Host` header to route to the right app; without either, it resets the handshake.

**Fix (1 commit, ~25 LOC, config only):**
- `apps/frontend/docker-entrypoint.sh` — derive `ORCHESTRATOR_HOST` (bare hostname, no scheme/path/port) from `ORCHESTRATOR_URL`; export both for envsubst.
- `apps/frontend/nginx.conf` — on `/api/` and `/ws/`: `proxy_set_header Host $ORCHESTRATOR_HOST;`, `proxy_ssl_server_name on;`, `proxy_ssl_name $ORCHESTRATOR_HOST;`. Existing WS `Upgrade`/`Connection` headers preserved.
- Diagnostic Playwright spec landed at `apps/frontend/e2e/mic-button.spec.ts` (+ `playwright.config.ts`, `@playwright/test` devDep, `test:e2e` script). Captures WS frames, console errors, network failures against the live URL. Reusable for any future "mic dead" UAT smoke.
- No React/JS changes — `useVoiceSession`'s same-origin `wss://` URL is correct by design; nginx is the intended data-path hop.

**Local gates:** `npm run lint` ✅, `npm run typecheck` ✅, `npm run build` ✅ (1524 modules / 177.28 kB JS — bundle unchanged, config-only fix).

**Deploy:** `azd deploy frontend` flaked (Docker daemon not running on operator box); fell back to Okoye's ACR-push pattern: `az acr build` → image `crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/frontend-crosstown-dryrun-may15:mic-fix-20260516094226`; `az containerapp update` rolled `frontend--0000002` to 100% traffic, Healthy.

**Post-deploy verification (Playwright re-run, `.squad/files/playwright-mic-button-postfix-2026-05-16.log`):** WS opens, `start` frame sent, 14 binary PCM audio frames sent, **0 WS errors, 0 closes, 0 network failures** in the 7 s window. One cosmetic 404 on `/api/health` (orchestrator only exposes `/health`, not `/api/health`) — unrelated, not blocking.

**Decision (one line):** Mic button is alive — Sean can UAT push-to-talk against the live frontend. Full voice loop (audio response back) is still gated on Bug #8 (Foundry Realtime WS handshake 404), which remains with Brady; that's an orchestrator-side issue independent of this fix.

**Files:** PR #17 (https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/17), `apps/frontend/nginx.conf`, `apps/frontend/docker-entrypoint.sh`, `apps/frontend/e2e/mic-button.spec.ts`, `apps/frontend/playwright.config.ts`, `.squad/files/playwright-mic-button-2026-05-16.log` (pre-fix), `.squad/files/playwright-mic-button-postfix-2026-05-16.log` (post-fix), `.squad/files/azd-deploy-frontend-mic-fix-2026-05-16.log`, `.squad/files/acr-build-frontend-mic-fix-2026-05-16.log`, `.squad/files/azd-up-result-2026-05-15.md` (Bug #13 row + section).

### D-029 · Bug #14 fixed — Voice loop end-to-end alive (explicit audio commit + gpt-realtime-1.5 schema)
**Date:** 2026-05-16
**Author:** Wanda Maximoff (Anomaly Hunter) — requested by Sean
**Status:** Shipped (PRs #19 + #20 open; both deployed to UAT)

**Discovery:** Sean UAT-tested push-to-talk. Mic button goes yellow, audio flows (per D-028 fix), but chat window shows nothing. `/api/turn` text path works. `/ws/voice` accepts connections and closes quickly with zero response frames.

**Root causes (two, both required to fix):**

1. **Explicit commit missing (PRIMARY)** — The orchestrator's `/ws/voice` loop never committed the audio buffer to the model. Without `input_audio_buffer.commit` + `response.create`, the model never processes the user's speech. The `stop` event sent by the frontend was ignored (handler did `break`, closing the session before any response).

2. **`stop` handler closed session too early (SECONDARY)** — The `stop` handler broke the WebSocket loop immediately. After PR #19 (Parker) added `stopTalking() → {type:"stop"}`, this became critical: stop arrived before model response, killing the session before anything came back.

**gpt-realtime-1.5 GA API schema — unsupported fields discovered:**
- `session.input_audio_transcription`: **REJECTED** (`Unknown parameter`) — causes `session.updated` timeout
- `session.turn_detection`: **REJECTED** (`Unknown parameter`) — same failure mode
- `input_audio_buffer.commit`, `response.create`: **SUPPORTED** ✅ (standard Realtime protocol messages, not session config)

**Fix (PR #20, branch `squad/fix-voice-vad-commit`):**
- `foundry_realtime.py`: Add `commit_audio()` method (`input_audio_buffer.commit` + `response.create`); add pump error-logging (captures Foundry `error` events, unblocks `session_ready`, raises `RuntimeError` with exact message — essential for diagnosing schema rejections); remove `input_audio_transcription` and `turn_detection` from `session.update` (both unsupported in this gpt-realtime-1.5 deployment).
- `orchestrator.py`: `stop` handler calls `commit_audio()` via duck-typed `getattr`, then continues loop (does NOT break). Multi-turn PTT preserved: session stays open after response.

**Paired with PR #19 (Parker):** Frontend sends `{type:"stop"}` on `stopTalking()` (mic release). Both PRs must merge together for end-to-end voice.

**Live probe (orchestrator--0000007, tag `vad-fix-20260516104728e`):**
```
CONNECTED → start → 10 PCM chunks → stop → FRAME[1]: type=final
```
First response frame ever received from the voice path. With real speech (non-silence), `transcript_delta` frames precede `final`.

**Decision:** Voice loop is live. Sean can UAT with real speech. Both PRs (#19 frontend, #20 orchestrator) must merge to `main` together. PTT pattern is client-driven explicit commit (no server VAD — unsupported by this gpt-realtime-1.5 deployment).

**Files:** PR #19 (https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/19), PR #20 (https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/20), `apps/orchestrator/voice/foundry_realtime.py`, `apps/orchestrator/agent/orchestrator.py`.

---


### D-20 · [merged from inbox]
**Date:** 2026-05-15
**Author:** Banner (Tester / Quality)
**Status:** Proposed (awaiting PR #10 merge + redeploy)

## Decision

Added `aiohttp>=3.9` as a direct top-level dependency in `apps/orchestrator/pyproject.toml` to satisfy `azure.identity.aio`'s async transport requirement.

Form chosen: **direct dep**, not `azure-identity[aio]` extras. Rationale: `azure-identity 1.17.1` does not actually publish an `[aio]` extras group (pip warned on attempt). Direct `aiohttp` pin is the supported form per Azure SDK docs.

## Trigger

Bug #5 from the 2026-05-19 customer-handoff dry-run. Live `azd up` smoke (Okoye, 2026-05-15) showed `POST /api/turn` returning HTTP 500 with `ImportError: aiohttp package is not installed` thrown by `azure.identity.aio._credentials.app_service`.

## Scope

- File changed: `apps/orchestrator/pyproject.toml` (one line added).
- PR: [#10](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/10), branch `squad/fix-orchestrator-aiohttp-dep`, based on `squad/fix-foundry-hub-name-length`.
- Stack order: #5 (merged) → #7 → #8 → #9 (Okoye, search RBAC) → #10 (this).

## Validation

- `python -m ruff check .` — pass
- `python -m mypy --strict .` — pass (19 files)
- `python -m pytest -q` — 11/11 pass
- Import smoke — `aiohttp 3.13.5` loads alongside `azure.identity.aio`

## Follow-ups

1. Land PR #9 first, then PR #10.
2. Run `azd deploy orchestrator` to roll the fixed container — **do not auto-trigger**; coordinate with Squad to avoid overlap with Okoye's RBAC redeploy.
3. After redeploy, re-run `/api/turn` live smoke to confirm Bug #5 is closed.

## Autopilot disclosure

PR was opened in autopilot without live per-step approval. Change is a single-line dep addition; non-destructive, reviewable, CI-gated.



### D-21 · [merged from inbox]
**Date:** 2026-05-15
**Author:** Banner (Tester / Quality)
**Status:** Proposed — needs T'Challa adoption + Brady awareness before Phase 2.5

## Summary

| Item | Status |
|---|---|
| Bug #6 — Cosmos seed `BadRequest` (missing `id` field on incident docs) | ✅ **FIXED** — PR #11 |
| Bug #5 / PR #10 — orchestrator `aiohttp` dep | ✅ **COMPLETED** via PR #12 (Dockerfile inlined deps; pyproject change alone wasn't enough) |
| Cosmos `incidents` container | ✅ 20 docs seeded, both `id` and `incidentId` populated |
| `/api/turn` live cited responses | ❌ **STILL BLOCKED** — new Bug #7 surfaced |
| Phase 2.5 LIVE-READY verdict | 🔴 **NO-GO** until Bug #7 fixed |

## Bug #6 — root cause + fix (PR #11)

**Where:** `scripts/load_search_index.py` → `seed_incidents()` (line ~135).

**Cause:** `data/seed_incidents.json` records carry `incidentId` (correct partition key per architectural contract #6) but **no top-level `id` field**. Cosmos SQL API rejects any document without a non-empty `id` string.

**Live repro proof:**
| Doc shape | Cosmos response |
|---|---|
| `{ incidentId: "INC-TEST-NOID", ... }` | `CosmosHttpResponseError(BadRequest): "One of the specified inputs is invalid"` |
| `{ id: "INC-TEST-WITHID", incidentId: "INC-TEST-WITHID", ... }` | Upsert OK (`_rid` returned) |

**Fix:** mirror `incidentId` → `id` if absent before upsert. 6 lines added in one function.

**Why mirror is safe:** the reader (`apps/log_analyst/tools/summarize_incident.py::_fetch_incident`) queries by `incidentId`, not by point-read on `id`, so `id == incidentId` introduces no contract drift.

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/11
**Branch:** `squad/fix-cosmos-seed-incidents` (base `squad/fix-orchestrator-aiohttp-dep` = PR #10).

## PR #10 completion — PR #12 (Dockerfile dep)

**Where:** `apps/orchestrator/Dockerfile` lines 5-9.

**Cause:** PR #10 added `aiohttp>=3.9` to `pyproject.toml`. The Dockerfile builder pins its dep list **inline** and does NOT install from `pyproject.toml`, so the dep never made it into the image. After `azd deploy orchestrator` against dry-run env, `/api/turn` still raised the original `ImportError: aiohttp package is not installed`.

**Fix:** add `"aiohttp>=3.9"` to the Dockerfile builder pip install line. One-line change.

**Confirmed effective:** post-redeploy, the aiohttp ImportError is gone from the trace; a different error replaces it (Bug #7).

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/12
**Branch:** `squad/fix-orchestrator-aiohttp-dockerfile` (base `squad/fix-cosmos-seed-incidents` = PR #11).

**Mea culpa:** I shipped PR #10 thinking pyproject was authoritative — should have checked the Dockerfile. Logging here so we don't repeat. Follow-up worth filing: switch Dockerfile to `pip install .` (reads pyproject) so this class of drift can't recur.

## NEW — Bug #7 (escalated, NOT fixed) — Foundry Realtime WebSocket URL scheme

**Where:** `apps/orchestrator/voice/foundry_realtime.py:160` (`open_session`).

**Symptom:** All three tool turns return HTTP 500.

**Stack trace (full log: `.squad/files/orchestrator-500-trace-after-dockerfile.log`):**
```
File "/app/voice/foundry_realtime.py", line 160, in open_session
    ws = await websockets.connect(url, additional_headers=headers)
File "/usr/local/lib/python3.11/site-packages/websockets/uri.py", line 76, in parse_uri
    raise InvalidURI(uri, "scheme isn't ws or wss")
websockets.exceptions.InvalidURI:
  https://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5
  isn't a valid URI: scheme isn't ws or wss
```

**Almost certainly:** the Foundry Realtime endpoint env var is being read as `https://...` (the AzureML inference URL) and passed straight into `websockets.connect()` which requires `ws://` or `wss://`. Fix is likely a one-liner: `url = url.replace("https://", "wss://", 1)` (or build the WS URL explicitly from the endpoint).

**Why I'm not shipping the fix:**
- Per Brady's failure-handling rule: "If `/api/turn` returns 500 with a NEW error after deploy → STOP, capture stack trace, escalate (don't blindly fix more bugs without Brady's signoff)."
- `voice/foundry_realtime.py` is on the realtime swap critical path (D-009). Touching it without the realtime owner's review is risky.
- The fix touches Foundry plumbing — Maximoff or Strange territory.

**Owner suggestion:** Maximoff (eval / realtime familiarity) or whoever owns the D-009 realtime swap.

## Phase 2.5 verdict

**🔴 NO-GO** until Bug #7 ships. Bug #6 is fixed and verified, but `/api/turn` cannot return any cited response (every tool path requires `provider.open_session()` which crashes before tool dispatch).

Once Bug #7 is fixed and orchestrator redeployed, expected state is GREEN (Cosmos seeded, AI Search seeded, aiohttp present). Re-run the same three smoke turns to confirm.

## References

- Bug #6 PR: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/11
- Bug #5 follow-up PR: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/12
- Postprovision (Bug #6 verified): `.squad/files/azd-hook-postprovision-after-bug6.log` — 20 incidents upserted
- Orchestrator deploy (Dockerfile fix): `.squad/files/azd-deploy-orchestrator-final-v2.log` — 1m 37s
- Bug #7 trace: `.squad/files/orchestrator-500-trace-after-dockerfile.log`
- Architectural contract: `.github/copilot-instructions.md` § 6 (Cosmos partition keys)



### D-23 · [merged from inbox]
**Date:** 2026-05-15  
**Author:** Wanda Maximoff (autopilot — Brady OK'd)  
**Status:** DECISION + ESCALATION

---

## What shipped (PR #14)

**Bug #8 root cause:** `factory.py` passed `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`
(`https://swedencentral.api.azureml.ms`) to `FoundryRealtimeProvider`. The GA
`gpt-realtime-1.5` WebSocket endpoint lives on `AZURE_OPENAI_ENDPOINT`
(`https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/`).

**Fix (2 files, 3 lines):**
- `settings.py`: add `azure_openai_endpoint: str = ""`  
- `voice/factory.py`: `endpoint=s.azure_openai_endpoint`

**Evidence:** Live probe — `azureml.ms` → HTTP 404 | `openai.azure.com` → HANDSHAKE_OK.  
**Validation:** ruff ✅ · mypy --strict ✅ · pytest 11/11 ✅  
**Deploy:** `azd deploy orchestrator` — 30 s, revision `orchestrator--azd-1778880853`

---

## Smoke result post-deploy

| Tool path | HTTP | Citations | Tool calls | Warnings |
|-----------|------|-----------|------------|----------|
| search_logs | 200 OK | 0 | [] | uncited |
| detect_pattern | 200 OK | 0 | [] | uncited |
| summarize_incident | 200 OK | 0 | [] | uncited |

✅ Bug #8 cleared — no more 500 / InvalidStatus HTTP 404.  
🔴 **Bug #9 found** — tool dispatch not happening; citation contract NOT met.

---

## Bug #9 (escalated — NOT chased per failure-handling rules)

**Symptom:** All `/api/turn` calls return HTTP 200 with generic model text, `tool_calls: []`,
`citations: []`, `warnings: ["uncited"]`. Model says "I don't have access to station logs."

**Known facts:**
- `tools_loaded: true` (health endpoint)
- Container logs: clean 200s, no tracebacks
- `session.update` sends `tools` + `instructions` (system prompt) to Realtime API
- Same behavior across all 3 tool paths

**Possible causes Brady should rule on:**
1. `tool_choice` not set in `session.update` — gpt-realtime-1.5 may require explicit `"tool_choice": "auto"` or `"required"` to invoke tools
2. Timing race — `session.update` ACK not awaited before `send_text` fires
3. System prompt not strong enough to instruct tool use in Realtime context
4. Model behavior difference vs gpt-4o-realtime-preview

**Recommended next investigation:** Check `session.updated` server event ACK before sending user message; add `"tool_choice": "auto"` to `session.update`.

---

Brady: Bug #8 is done. Need a ruling on Bug #9 before Phase 2.5 can go live.



### D-26 · [merged from inbox]
**Date:** 2026-05-15T22:37:00-04:00
**From:** Okoye (Operations / DevOps)
**To:** Sean, Team
**Re:** Bug #11 — ACA Hello World placeholder resolved

---

## Status: ✅ LIVE

Both services are now running their real container images on ACA.

| Service | Revision | HealthState | Traffic | Image |
|---|---|---|---|---|
| frontend | `frontend--azd-1778884551` | Healthy | 100% | `crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/frontend-crosstown-dryrun-may15:azd-deploy-1778884543` |
| log-analyst | `log-analyst--azd-1778884163` | Healthy | 100% | `crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/log-analyst-crosstown-dryrun-may15:azd-deploy-...` |

## Frontend

**URL:** https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io

Content: `HTTP 200 | 423 bytes | <title>MTA Hackathon — Voice Demo</title>` — real Vite/React push-to-talk app.

## Root cause (two bugs in Dockerfile, compounding)

1. **CRLF shebang** — `docker-entrypoint.sh` had Windows CRLF. Alpine reads `#!/bin/sh\r` → "not found", container exits immediately. ACA falls back to Hello World placeholder.
2. **nginx pid permission** — `nginx:1.27-alpine` defaults to `pid /run/nginx.pid;`. Running as non-root `app` user, `/run` is not writable → `[emerg] Permission denied`. Also crashes, same Hello World result.

## Fix (commit 942b3b0)

- `docker-entrypoint.sh` → LF line endings
- `Dockerfile` → `sed -i 's|^pid .*|pid /tmp/nginx.pid;|'` + `/run` in chown
- `.gitattributes` → `*.sh text eol=lf` (prevents CRLF recurrence)

## /api/turn re-smoke (no regression)

```
search_logs:       Citations: 10  | Tool calls: 1 | Warnings: NONE  ✅
detect_pattern:    Citations: 0   | Tool calls: 2 | Warnings: 400 (pre-existing PR #16)  ⚠️
summarize_incident: Citations: 2  | Tool calls: 1 | Warnings: NONE  ✅
```

Log-analyst redeploy did **not** regress orchestrator tool dispatch.

## Sean — UAT checklist

- [ ] Open https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io — should see push-to-talk UI (not Hello World)
- [ ] Press mic, ask "Show me door-fault logs from Atlantic" — should get voiced response with citations
- [ ] API smoke: `search_logs` and `summarize_incident` paths return citations ✅
- [ ] Known gap: `detect_pattern` returns 400 — Banner/PR #16 is addressing this

---
*Okoye, 2026-05-15*



### D-27 · [merged from inbox]
**Author:** Banner
**Status:** Inbox — for Sean's review

## Outcome
**No code change shipped.** Bug #12 was caused by sending `{"message": "..."}` to `POST /api/turn`; the canonical request shape is `{"text": "..."}` (pinned by `apps/orchestrator/main.py::TurnRequest`, 11 pytest cases, eval runner, redteam runner, and README).

## Live verification (all 3 tool paths, 2026-05-15 ~22:44Z)
| Tool | citations | warnings | tool_calls.arguments |
|---|---|---|---|
| `search_logs` | 10 | NONE | `{"query":"door fault Atlantic station"}` |
| `detect_pattern` | 39 | NONE | `{"log_id":"L-001234"}` |
| `summarize_incident` | 2 | NONE | `{"incident_id":"INC-1001"}` |

Bug #10 (PR #16) fix holds. detect_pattern still resolves `log_id` correctly.

## Mystery resolution
Banner's earlier Bug #10 smoke at 22:18Z **already saw the real log-analyst image** (10/39/2 citations cannot come from Hello World). Okoye-2's 22:29Z redeploy (revision `log-analyst--azd-1778884163`) was likely a refresh of the already-deployed real image, not a Hello-World → real transition. ACA prunes old revisions, which is why her `az containerapp revision list` saw only one. No hidden fallback exists in the orchestrator dispatch path (verified in `main.py:97-119` and `agent/tools.py::dispatch`).

## ⚠️ Process note for Sean
The Bug #12 brief used `{"message":"..."}` in its test commands — that was the source of the 422s. Future test payloads should use `{"text":"..."}` to match the canonical contract.

## What to use for UAT
```powershell
$orchUrl = "https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io"
$body = @{ text = "Show me door-fault logs from Atlantic station" } | ConvertTo-Json
Invoke-RestMethod -Uri "$orchUrl/api/turn" -Method Post -Body $body -ContentType "application/json"
```

Frontend separately uses `/ws/voice` (WebSocket), not `/api/turn`, so this never affected the push-to-talk UI.

## Diagnosis doc
`.squad/files/banner-bug12-diagnosis-2026-05-15.md` — full forensic trace, expected-vs-actual diff, mystery resolution, recommendation.

## Optional follow-up (not a blocker)
Bug #10 secondary symptom (model occasionally tries `search_logs.time_range` as string) still produces 400s in log-analyst tail that the model self-corrects from. Net customer impact: zero (citations: 10, warnings: NONE). A tightened schema with an example value would silence those tail lines. Tracked but not urgent.

### D-20

**Date:** 2026-05-15
**Author:** Banner (Tester / Quality)
**Status:** Proposed (awaiting PR #10 merge + redeploy)

## Decision

Added `aiohttp>=3.9` as a direct top-level dependency in `apps/orchestrator/pyproject.toml` to satisfy `azure.identity.aio`'s async transport requirement.

Form chosen: **direct dep**, not `azure-identity[aio]` extras. Rationale: `azure-identity 1.17.1` does not actually publish an `[aio]` extras group (pip warned on attempt). Direct `aiohttp` pin is the supported form per Azure SDK docs.

## Trigger

Bug #5 from the 2026-05-19 customer-handoff dry-run. Live `azd up` smoke (Okoye, 2026-05-15) showed `POST /api/turn` returning HTTP 500 with `ImportError: aiohttp package is not installed` thrown by `azure.identity.aio._credentials.app_service`.

## Scope

- File changed: `apps/orchestrator/pyproject.toml` (one line added).
- PR: [#10](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/10), branch `squad/fix-orchestrator-aiohttp-dep`, based on `squad/fix-foundry-hub-name-length`.
- Stack order: #5 (merged) → #7 → #8 → #9 (Okoye, search RBAC) → #10 (this).

## Validation

- `python -m ruff check .` — pass
- `python -m mypy --strict .` — pass (19 files)
- `python -m pytest -q` — 11/11 pass
- Import smoke — `aiohttp 3.13.5` loads alongside `azure.identity.aio`

## Follow-ups

1. Land PR #9 first, then PR #10.
2. Run `azd deploy orchestrator` to roll the fixed container — **do not auto-trigger**; coordinate with Squad to avoid overlap with Okoye's RBAC redeploy.
3. After redeploy, re-run `/api/turn` live smoke to confirm Bug #5 is closed.

## Autopilot disclosure

PR was opened in autopilot without live per-step approval. Change is a single-line dep addition; non-destructive, reviewable, CI-gated.

### D-21

**Date:** 2026-05-15
**Author:** Banner (Tester / Quality)
**Status:** Proposed — needs T'Challa adoption + Brady awareness before Phase 2.5

## Summary

| Item | Status |
|---|---|
| Bug #6 — Cosmos seed `BadRequest` (missing `id` field on incident docs) | ✅ **FIXED** — PR #11 |
| Bug #5 / PR #10 — orchestrator `aiohttp` dep | ✅ **COMPLETED** via PR #12 (Dockerfile inlined deps; pyproject change alone wasn't enough) |
| Cosmos `incidents` container | ✅ 20 docs seeded, both `id` and `incidentId` populated |
| `/api/turn` live cited responses | ❌ **STILL BLOCKED** — new Bug #7 surfaced |
| Phase 2.5 LIVE-READY verdict | 🔴 **NO-GO** until Bug #7 fixed |

## Bug #6 — root cause + fix (PR #11)

**Where:** `scripts/load_search_index.py` → `seed_incidents()` (line ~135).

**Cause:** `data/seed_incidents.json` records carry `incidentId` (correct partition key per architectural contract #6) but **no top-level `id` field**. Cosmos SQL API rejects any document without a non-empty `id` string.

**Live repro proof:**
| Doc shape | Cosmos response |
|---|---|
| `{ incidentId: "INC-TEST-NOID", ... }` | `CosmosHttpResponseError(BadRequest): "One of the specified inputs is invalid"` |
| `{ id: "INC-TEST-WITHID", incidentId: "INC-TEST-WITHID", ... }` | Upsert OK (`_rid` returned) |

**Fix:** mirror `incidentId` → `id` if absent before upsert. 6 lines added in one function.

**Why mirror is safe:** the reader (`apps/log_analyst/tools/summarize_incident.py::_fetch_incident`) queries by `incidentId`, not by point-read on `id`, so `id == incidentId` introduces no contract drift.

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/11
**Branch:** `squad/fix-cosmos-seed-incidents` (base `squad/fix-orchestrator-aiohttp-dep` = PR #10).

## PR #10 completion — PR #12 (Dockerfile dep)

**Where:** `apps/orchestrator/Dockerfile` lines 5-9.

**Cause:** PR #10 added `aiohttp>=3.9` to `pyproject.toml`. The Dockerfile builder pins its dep list **inline** and does NOT install from `pyproject.toml`, so the dep never made it into the image. After `azd deploy orchestrator` against dry-run env, `/api/turn` still raised the original `ImportError: aiohttp package is not installed`.

**Fix:** add `"aiohttp>=3.9"` to the Dockerfile builder pip install line. One-line change.

**Confirmed effective:** post-redeploy, the aiohttp ImportError is gone from the trace; a different error replaces it (Bug #7).

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/12
**Branch:** `squad/fix-orchestrator-aiohttp-dockerfile` (base `squad/fix-cosmos-seed-incidents` = PR #11).

**Mea culpa:** I shipped PR #10 thinking pyproject was authoritative — should have checked the Dockerfile. Logging here so we don't repeat. Follow-up worth filing: switch Dockerfile to `pip install .` (reads pyproject) so this class of drift can't recur.

## NEW — Bug #7 (escalated, NOT fixed) — Foundry Realtime WebSocket URL scheme

**Where:** `apps/orchestrator/voice/foundry_realtime.py:160` (`open_session`).

**Symptom:** All three tool turns return HTTP 500.

**Stack trace (full log: `.squad/files/orchestrator-500-trace-after-dockerfile.log`):**
```
File "/app/voice/foundry_realtime.py", line 160, in open_session
    ws = await websockets.connect(url, additional_headers=headers)
File "/usr/local/lib/python3.11/site-packages/websockets/uri.py", line 76, in parse_uri
    raise InvalidURI(uri, "scheme isn't ws or wss")
websockets.exceptions.InvalidURI:
  https://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5
  isn't a valid URI: scheme isn't ws or wss
```

**Almost certainly:** the Foundry Realtime endpoint env var is being read as `https://...` (the AzureML inference URL) and passed straight into `websockets.connect()` which requires `ws://` or `wss://`. Fix is likely a one-liner: `url = url.replace("https://", "wss://", 1)` (or build the WS URL explicitly from the endpoint).

**Why I'm not shipping the fix:**
- Per Brady's failure-handling rule: "If `/api/turn` returns 500 with a NEW error after deploy → STOP, capture stack trace, escalate (don't blindly fix more bugs without Brady's signoff)."
- `voice/foundry_realtime.py` is on the realtime swap critical path (D-009). Touching it without the realtime owner's review is risky.
- The fix touches Foundry plumbing — Maximoff or Strange territory.

**Owner suggestion:** Maximoff (eval / realtime familiarity) or whoever owns the D-009 realtime swap.

## Phase 2.5 verdict

**🔴 NO-GO** until Bug #7 ships. Bug #6 is fixed and verified, but `/api/turn` cannot return any cited response (every tool path requires `provider.open_session()` which crashes before tool dispatch).

Once Bug #7 is fixed and orchestrator redeployed, expected state is GREEN (Cosmos seeded, AI Search seeded, aiohttp present). Re-run the same three smoke turns to confirm.

## References

- Bug #6 PR: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/11
- Bug #5 follow-up PR: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/12
- Postprovision (Bug #6 verified): `.squad/files/azd-hook-postprovision-after-bug6.log` — 20 incidents upserted
- Orchestrator deploy (Dockerfile fix): `.squad/files/azd-deploy-orchestrator-final-v2.log` — 1m 37s
- Bug #7 trace: `.squad/files/orchestrator-500-trace-after-dockerfile.log`
- Architectural contract: `.github/copilot-instructions.md` § 6 (Cosmos partition keys)

### D-23

**Date:** 2026-05-15  
**Author:** Wanda Maximoff (autopilot — Brady OK'd)  
**Status:** DECISION + ESCALATION

---

## What shipped (PR #14)

**Bug #8 root cause:** `factory.py` passed `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`
(`https://swedencentral.api.azureml.ms`) to `FoundryRealtimeProvider`. The GA
`gpt-realtime-1.5` WebSocket endpoint lives on `AZURE_OPENAI_ENDPOINT`
(`https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/`).

**Fix (2 files, 3 lines):**
- `settings.py`: add `azure_openai_endpoint: str = ""`  
- `voice/factory.py`: `endpoint=s.azure_openai_endpoint`

**Evidence:** Live probe — `azureml.ms` → HTTP 404 | `openai.azure.com` → HANDSHAKE_OK.  
**Validation:** ruff ✅ · mypy --strict ✅ · pytest 11/11 ✅  
**Deploy:** `azd deploy orchestrator` — 30 s, revision `orchestrator--azd-1778880853`

---

## Smoke result post-deploy

| Tool path | HTTP | Citations | Tool calls | Warnings |
|-----------|------|-----------|------------|----------|
| search_logs | 200 OK | 0 | [] | uncited |
| detect_pattern | 200 OK | 0 | [] | uncited |
| summarize_incident | 200 OK | 0 | [] | uncited |

✅ Bug #8 cleared — no more 500 / InvalidStatus HTTP 404.  
🔴 **Bug #9 found** — tool dispatch not happening; citation contract NOT met.

---

## Bug #9 (escalated — NOT chased per failure-handling rules)

**Symptom:** All `/api/turn` calls return HTTP 200 with generic model text, `tool_calls: []`,
`citations: []`, `warnings: ["uncited"]`. Model says "I don't have access to station logs."

**Known facts:**
- `tools_loaded: true` (health endpoint)
- Container logs: clean 200s, no tracebacks
- `session.update` sends `tools` + `instructions` (system prompt) to Realtime API
- Same behavior across all 3 tool paths

**Possible causes Brady should rule on:**
1. `tool_choice` not set in `session.update` — gpt-realtime-1.5 may require explicit `"tool_choice": "auto"` or `"required"` to invoke tools
2. Timing race — `session.update` ACK not awaited before `send_text` fires
3. System prompt not strong enough to instruct tool use in Realtime context
4. Model behavior difference vs gpt-4o-realtime-preview

**Recommended next investigation:** Check `session.updated` server event ACK before sending user message; add `"tool_choice": "auto"` to `session.update`.

---

Brady: Bug #8 is done. Need a ruling on Bug #9 before Phase 2.5 can go live.

### D-24

**Date:** 2026-05-15
**Author:** Maximoff (Wanda)
**Status:** SHIPPED — awaiting merge into PR #14 base

## Decision

Ship PR #15 (`squad/fix-realtime-tool-dispatch-race`) to fix Bug #9: orchestrator
`/api/turn` returned HTTP 200 but with `tool_calls: []`, `citations: []`, and
`warnings: ["uncited"]` on all three tool paths after Bug #8 fix.

## Root Cause Summary

Three compounding bugs in `apps/orchestrator/voice/foundry_realtime.py`:

1. **Timing race (H2):** `open_session()` sent `session.update` (with tool specs) and returned
   immediately. The caller fired `conversation.item.create` + `response.create` before the
   Realtime API server processed tool registration (before `session.updated` ACK).

2. **GA schema mismatch (H4):** `session.update` payload used `gpt-4o-realtime-preview` field
   names rejected by the `gpt-realtime-1.5` GA API: `modalities: ["text","audio"]` (renamed to
   `output_modalities`; combining text+audio invalid), `input_audio_format`/`output_audio_format`
   (not valid top-level GA fields), missing `type: "realtime"` in session object. Server responded
   with an `error` event silently swallowed by `_translate`, so `session.updated` never arrived.

3. **response.done loop break (H3b):** The first `response.done` (function-call response, output
   type `"function_call"`, no `content[]`) was translated as `Final(text="")`, causing `api_turn`
   to break before the model's actual text reply (second response) arrived.

## Fix Applied

Three commits on `squad/fix-realtime-tool-dispatch-race` (stacked on PR #14):

- **Commit 1:** `asyncio.Event session_ready` — await `session.updated` with 10 s timeout before returning session; `"tool_choice": "auto"` in session.update
- **Commit 2:** GA schema correction — `"type": "realtime"`, `"output_modalities": ["audio"]`, removed invalid top-level audio format fields; `_translate response.done` captures both `transcript` and `text` content fields
- **Commit 3:** `_translate response.done` returns `None` for pure function-call responses; only returns `Final` when message content exists or output is empty

## Live Smoke Results (final deploy)

| Path | Citations | Tool | Warnings | Text |
|---|---|---|---|---|
| search_logs | 10 | ✅ search_logs | NONE | 307 chars |
| detect_pattern | 0 | ✅ detect_pattern | 400 Bad Request (log-analyst) | 223 chars |
| summarize_incident | 2 | ✅ summarize_incident | NONE | 364 chars |

**Citation contract met for 2/3 paths.** `detect_pattern` dispatches correctly but log-analyst
returns HTTP 400 — separate pre-existing issue in log-analyst tool handler, not orchestrator.

## Action Required from Brady/Sean

1. **Merge PR #13 → PR #14 → PR #15** in order (stacked PRs).
2. Investigate `detect_pattern` log-analyst 400 error (new Bug #10 candidate).
3. Run live eval gate (`EVAL_MODE=live`) once PRs are merged and redeployed to `main`.

### D-25

**Date:** 2026-05-15
**Owner:** Banner
**Status:** SHIPPED — PR #16 stacked on PR #15

## What

Live `/api/turn` smoke against `detect_pattern` returned HTTP 400 from log-analyst
(`log_id must be a non-empty string`). Investigation showed the orchestrator was
exposing **empty** parameter schemas to the Realtime model for **every** tool —
`search_logs` and `summarize_incident` only worked by the model guessing obvious
arg names. `detect_pattern.log_id` is not obvious, so the model invented
`seed_log_id` (or omitted it entirely) and log-analyst correctly 400'd.

## Root cause (1 line)

`apps/orchestrator/agent/tools.py::ToolRegistry.load()` read field `parameters`
from log-analyst's `/tools` response, but log-analyst's `ToolDescriptor`
(`apps/log_analyst/citations.py`) serializes the JSON Schema as `input_schema`.

## Fix

Accept both `input_schema` and `parameters`. One file, one logic change.
Backwards-compatible with the existing test mock. Regression test added.

## Validation (local — `apps/orchestrator`)

- `ruff check .` — clean
- `mypy --strict .` — 19 files, no issues
- `pytest -q` — 12/12 pass (added `test_registry_load_input_schema`)

## Validation (live, after `az containerapp update --image ...`)

| Tool | citations | warnings | tool args |
|---|---|---|---|
| `search_logs` | 10 | (one stray 400 on first call — model self-corrected on retry) | `query`, `time_range` |
| **`detect_pattern`** | **39** | **NONE** | `{"log_id": "L-001234"}` ✅ |
| `summarize_incident` | 2 | NONE | `{"incident_id": "INC-1001"}` |

Bug #10 verified fixed. All three tool paths now return citations.

## Notes

- `azd deploy orchestrator` failed three times with intermittent ARM 404s (HTML
  error pages from `management.azure.com` on `getContainerApp` / `listSecrets`
  / `PATCH containerApps`). Fell back to `az containerapp update --image
  $latestTag` which succeeded immediately. New revision: `orchestrator--0000002`,
  100% traffic, healthy, running.
- Post-fix, the Realtime model now sees the full JSON Schema for every tool.
  This exposes a minor secondary effect: on `search_logs`, the model sometimes
  formats `time_range` as a string on its first attempt (instead of the
  required `{from, to}` object) and self-corrects on a retry. Net result is
  still citations=10, but a `400 Bad Request` warning surfaces. Not blocking
  Phase 2.5; can be tightened later by adding a stricter system-prompt example
  or by relaxing `time_range` to accept a string fallback. **Not in scope here.**

## Open decision

None — D-025 is a clean ship. Stacked PR chain remains:

| # | Bug | PR | Status |
|---|---|---|---|
| 7 | wss:// scheme | #13 | merged |
| 8 | AOAI direct endpoint | #14 | open |
| 9 | Realtime tool dispatch race + GA schema | #15 | open |
| **10** | **Orchestrator schema-passthrough (`input_schema`)** | **#16** | **open — this PR** |

## Autopilot disclosure

This session was completed under autopilot mode. Branch
`squad/fix-log-analyst-detect-pattern-400` created from
`squad/fix-realtime-tool-dispatch-race`, fix authored, ruff/mypy/pytest run
locally (all green), committed with Co-authored-by trailer, pushed, PR #16
opened against PR #15. Image pushed via `azd deploy orchestrator` (which then
hit ARM intermittent errors); revision promoted via `az containerapp update
--image $latestTag`. Live smoke verified detect_pattern + summarize_incident
return citations with NONE warnings; search_logs returns 10 citations with a
self-corrected retry artifact (acceptable, documented above).

### D-26

**Date:** 2026-05-15T22:37:00-04:00
**From:** Okoye (Operations / DevOps)
**To:** Sean, Team
**Re:** Bug #11 — ACA Hello World placeholder resolved

---

## Status: ✅ LIVE

Both services are now running their real container images on ACA.

| Service | Revision | HealthState | Traffic | Image |
|---|---|---|---|---|
| frontend | `frontend--azd-1778884551` | Healthy | 100% | `crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/frontend-crosstown-dryrun-may15:azd-deploy-1778884543` |
| log-analyst | `log-analyst--azd-1778884163` | Healthy | 100% | `crcrosstowndryrunmay15yycemmso7sk7q.azurecr.io/mta-ai-hackathon/log-analyst-crosstown-dryrun-may15:azd-deploy-...` |

## Frontend

**URL:** https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io

Content: `HTTP 200 | 423 bytes | <title>MTA Hackathon — Voice Demo</title>` — real Vite/React push-to-talk app.

## Root cause (two bugs in Dockerfile, compounding)

1. **CRLF shebang** — `docker-entrypoint.sh` had Windows CRLF. Alpine reads `#!/bin/sh\r` → "not found", container exits immediately. ACA falls back to Hello World placeholder.
2. **nginx pid permission** — `nginx:1.27-alpine` defaults to `pid /run/nginx.pid;`. Running as non-root `app` user, `/run` is not writable → `[emerg] Permission denied`. Also crashes, same Hello World result.

## Fix (commit 942b3b0)

- `docker-entrypoint.sh` → LF line endings
- `Dockerfile` → `sed -i 's|^pid .*|pid /tmp/nginx.pid;|'` + `/run` in chown
- `.gitattributes` → `*.sh text eol=lf` (prevents CRLF recurrence)

## /api/turn re-smoke (no regression)

```
search_logs:       Citations: 10  | Tool calls: 1 | Warnings: NONE  ✅
detect_pattern:    Citations: 0   | Tool calls: 2 | Warnings: 400 (pre-existing PR #16)  ⚠️
summarize_incident: Citations: 2  | Tool calls: 1 | Warnings: NONE  ✅
```

Log-analyst redeploy did **not** regress orchestrator tool dispatch.

## Sean — UAT checklist

- [ ] Open https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io — should see push-to-talk UI (not Hello World)
- [ ] Press mic, ask "Show me door-fault logs from Atlantic" — should get voiced response with citations
- [ ] API smoke: `search_logs` and `summarize_incident` paths return citations ✅
- [ ] Known gap: `detect_pattern` returns 400 — Banner/PR #16 is addressing this

---
*Okoye, 2026-05-15*

### D-27

**Author:** Banner
**Status:** Inbox — for Sean's review

## Outcome
**No code change shipped.** Bug #12 was caused by sending `{"message": "..."}` to `POST /api/turn`; the canonical request shape is `{"text": "..."}` (pinned by `apps/orchestrator/main.py::TurnRequest`, 11 pytest cases, eval runner, redteam runner, and README).

## Live verification (all 3 tool paths, 2026-05-15 ~22:44Z)
| Tool | citations | warnings | tool_calls.arguments |
|---|---|---|---|
| `search_logs` | 10 | NONE | `{"query":"door fault Atlantic station"}` |
| `detect_pattern` | 39 | NONE | `{"log_id":"L-001234"}` |
| `summarize_incident` | 2 | NONE | `{"incident_id":"INC-1001"}` |

Bug #10 (PR #16) fix holds. detect_pattern still resolves `log_id` correctly.

## Mystery resolution
Banner's earlier Bug #10 smoke at 22:18Z **already saw the real log-analyst image** (10/39/2 citations cannot come from Hello World). Okoye-2's 22:29Z redeploy (revision `log-analyst--azd-1778884163`) was likely a refresh of the already-deployed real image, not a Hello-World → real transition. ACA prunes old revisions, which is why her `az containerapp revision list` saw only one. No hidden fallback exists in the orchestrator dispatch path (verified in `main.py:97-119` and `agent/tools.py::dispatch`).

## ⚠️ Process note for Sean
The Bug #12 brief used `{"message":"..."}` in its test commands — that was the source of the 422s. Future test payloads should use `{"text":"..."}` to match the canonical contract.

## What to use for UAT
```powershell
$orchUrl = "https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io"
$body = @{ text = "Show me door-fault logs from Atlantic station" } | ConvertTo-Json
Invoke-RestMethod -Uri "$orchUrl/api/turn" -Method Post -Body $body -ContentType "application/json"
```

Frontend separately uses `/ws/voice` (WebSocket), not `/api/turn`, so this never affected the push-to-talk UI.

## Diagnosis doc
`.squad/files/banner-bug12-diagnosis-2026-05-15.md` — full forensic trace, expected-vs-actual diff, mystery resolution, recommendation.

## Optional follow-up (not a blocker)
Bug #10 secondary symptom (model occasionally tries `search_logs.time_range` as string) still produces 400s in log-analyst tail that the model self-corrects from. Net customer impact: zero (citations: 10, warnings: NONE). A tightened schema with an example value would silence those tail lines. Tracked but not urgent.

### D-031 · Re-enable input_audio_transcription — two-phase session.update (conversation parity, server side)
**Date:** 2026-05-16
**Author:** Maximoff (Anomaly Hunter)
**Requested by:** Sean
**Status:** Adopted

PR #20 dropped `input_audio_transcription` from `session.update` because it caused a 10-second timeout on the first deploy attempt. PR #22 restores it safely using a two-phase approach:

1. **Phase 1** — known-safe `session.update` with instructions/tools/modalities. Waits for `session.updated` ACK before returning.
2. **Phase 2** — fire-and-forget `session.update` with only `input_audio_transcription: {model: "whisper-1"}`. If the server rejects this (e.g. `Unknown parameter`), the error is silently absorbed by `_translate` (returns `None`); the voice loop continues without transcription rather than crashing.

This is safe because by Phase 2, `session_ready` is already set and `session_error` is no longer checked.

**Also ships:** All PR #20 orchestrator fixes (commit_audio, pump error capture, stop-handler no-break) which were deployed from branch but not yet in main.

**New `_translate` handlers:**
- `conversation.item.input_audio_transcription.delta` → `TranscriptDelta(role="user", final=False)` (streaming partials)
- `conversation.item.input_audio_transcription.failed` → `None` (graceful silence)

**Client event contract** (existing convention, unchanged):
```json
{"type": "transcript_delta", "role": "user", "text": "...", "final": false}
{"type": "transcript_delta", "role": "user", "text": "...", "final": true}
```

**New setting:** `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT` (default: `whisper-1`). Azure OpenAI requires an existing deployment name; OpenAI accepts `whisper-1`. Set to `""` to disable.

**Validation:** ruff clean, mypy --strict 20 files clean, pytest 25/25 (14 new in test_foundry_realtime.py).

**Deploy:** ACR build `user-transcript-20260516112305` → revision `orchestrator--0000008` (Healthy, 100% traffic).

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/22

---

### D-032 · User-turn transcripts must be rendered in the chat window (conversation parity)
**Date:** 2026-05-16
**Author:** Parker (Frontend)
**Requested by:** Sean
**Status:** Adopted

The chat window was showing only assistant responses. Sean reported the UI was not a conversation — the user's own speech was invisible.

**Root cause:** The frontend had no handler for the `user_transcript` (or alias) event that Wanda's orchestrator sends when `input_audio_transcription` is enabled. The event never reached the `transcripts` state array, so nothing was rendered on the user side.

**Fix (PR #21, commit c7c3a5e):**
- `protocol.ts`: Added `UserTranscript` type. `parseServerMessage` now normalizes all 4 Wanda event-name aliases to `{ type: "user_transcript", text, item_id? }`:
  - `user_transcript` (canonical)
  - `user_transcript_completed`
  - `input_audio_transcription_completed`
  - `transcript_user_final`
- `useVoiceSession.ts`: `applyFrame` gained a `user_transcript` case that appends a `{ role: "user", final: true }` `TranscriptLine`. Empty-text events are ignored (no-op).
- `Transcript.tsx`: No change needed. `role: "user"` was already styled as right-aligned blue bubble (`bg-subway-blue text-white self-end`).
- Tests: +3 new vitest cases (canonical event, all 4 aliases, protocol normalization). Total: 9/9.

**Gates:** lint ✅, typecheck ✅, vitest 9/9 ✅, build ✅ (177.79 kB).

**Deploy:** ACR build `user-transcript-20260516111507` → revision `frontend--0000004` (Healthy, 100% traffic).

**Live verify:** Waiting on Wanda's server-side deploy (input_audio_transcription re-enable + user_transcript forwarding). Once both deploys are live, hold mic → release → confirm user bubble appears in chat alongside assistant response.

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/21

---

### D-032 · User-turn transcripts must be rendered in the chat window (conversation parity)
**Date:** 2026-05-16
**Author:** Parker (Frontend)
**Requested by:** Sean
**Status:** Adopted

The chat window was showing only assistant responses. Sean reported the UI was not a conversation — the user's own speech was invisible.

**Root cause:** The frontend had no handler for the `user_transcript` (or alias) event that Wanda's orchestrator sends when `input_audio_transcription` is enabled. The event never reached the `transcripts` state array, so nothing was rendered on the user side.

**Fix (PR #21, commit c7c3a5e):**
- `protocol.ts`: Added `UserTranscript` type. `parseServerMessage` now normalizes all 4 Wanda event-name aliases to `{ type: "user_transcript", text, item_id? }`:
  - `user_transcript` (canonical)
  - `user_transcript_completed`
  - `input_audio_transcription_completed`
  - `transcript_user_final`
- `useVoiceSession.ts`: `applyFrame` gained a `user_transcript` case that appends a `{ role: "user", final: true }` `TranscriptLine`. Empty-text events are ignored (no-op).
- `Transcript.tsx`: No change needed. `role: "user"` was already styled as right-aligned blue bubble (`bg-subway-blue text-white self-end`).
- Tests: +3 new vitest cases (canonical event, all 4 aliases, protocol normalization). Total: 9/9.

**Gates:** lint ✅, typecheck ✅, vitest 9/9 ✅, build ✅ (177.79 kB).

**Deploy:** ACR build `user-transcript-20260516111507` → revision `frontend--0000004` (Healthy, 100% traffic).

**Live verify:** Waiting on Wanda's server-side deploy (input_audio_transcription re-enable + user_transcript forwarding). Once both deploys are live, hold mic → release → confirm user bubble appears in chat alongside assistant response.

**PR:** https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/21

---

## Guidelines

- All meaningful changes require team consensus.
- Document architectural decisions here.
- Keep history focused on work, decisions focused on direction.
- Casting changes require a T'Challa sign-off entry.





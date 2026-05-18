# Deploy workflow diagnosis — 2026-05-17
**Investigator:** Wanda (Maximoff)
**Failing runs:** 25999139361 (18:29 UTC, sha d0abd0a), 25999032995 (18:24 UTC, sha 6e86386)
**Last green deploy:** **none on record** — `gh run list --workflow=deploy --status=success` returns `[]`. The deploy workflow has never succeeded since the `environment: dev` change landed; all five most-recent runs (back to 15:11 UTC) fail identically at the OIDC login step.

## Root cause
🟡 **CONFIG DRIFT — OIDC federated identity credential is missing a subject for `environment:dev`.** The deploy job declares `environment: dev` (deploy.yml line 26), so GitHub mints an OIDC token whose `sub` claim is `repo:DevPost-Test-Hackathon/crosstown-app:environment:dev`. Entra rejects it with **AADSTS700213 — "No matching federated identity record found for presented assertion subject 'repo:DevPost-Test-Hackathon/crosstown-app:environment:dev'"**. The Entra app `b2451691-200c-4d8d-b50f-a60396ddb606` (tenant `9b7cbd77-6d6b-4879-8aba-63d7dfb18472`) does have *some* federated credential — almost certainly the original `ref:refs/heads/main` subject from before the deploy-hygiene refactor — but no credential whose subject pattern matches `environment:dev`. Nothing in the repo's code or Bicep is broken; this is purely an Azure-side identity configuration gap that must be added in the Entra app's "Federated credentials" blade. Job never reaches `azd provision` or `azd deploy`, so no infra/container/test failure is in play. The `apps/judging/` `azure.yaml` is *not* a factor — the workflow dies before any `azd` command that would resolve services.

## Evidence
- `gh run view 25999139361 --log-failed` — step **"Log in (OIDC)"** fails in 13s with:
  - `ERROR: Authentication with Azure failed.`
  - `ClientAssertionCredential authentication failed.`
  - `POST https://login.microsoftonline.com/9b7cbd77-6d6b-4879-8aba-63d7dfb18472/oauth2/v2.0/token` → **`RESPONSE 401: 401 Unauthorized`**
  - `"error": "invalid_client"`, `"error_codes": [700213]`
  - `"error_description": "AADSTS700213: No matching federated identity record found for presented assertion subject 'repo:DevPost-Test-Hackathon/crosstown-app:environment:dev'."`
  - Trace ID `c71e2126-e487-4b03-98cf-51f9fda94400`, Correlation ID `91497e24-da34-461b-8e43-c7f80911ea1e`.
- `.github/workflows/deploy.yml:26` — `environment: dev` (added by PR #29). This is what drives the `environment:dev` subject claim.
- `.github/workflows/deploy.yml:51-59` — login step passes `AZURE_CLIENT_ID=${{ vars.AZURE_CLIENT_ID }}` (`b2451691-200c-4d8d-b50f-a60396ddb606`) and `AZURE_TENANT_ID=${{ vars.AZURE_TENANT_ID }}` — both repo vars resolve, so the failure is not a missing variable; the token is minted and *rejected by Entra*.
- All 5 most-recent failed runs (25999139361, 25999032995, 25998917601, 25998867451, 25994549401) fail at the same step. The earliest failure (15:11 UTC, sha 2276017 — Okoye's PR #22 ship-it commit) is the **first push to main after** the deploy-hygiene merge that introduced `environment: dev`. The pattern is deterministic, not flaky → not 🔵 transient.
- `gh run list --workflow=deploy --status=success` → `[]` (no successful run exists post-`environment:dev`).

## Suspected commit
**`3398440` — "chore(deploy): deploy-hygiene bundle — smoke + healthchecks + nginx + main-only guard + cassettes (#29)"** (merged from `ea17f2a`, Sat May 16 20:23 -0400). `git show 3398440 -- .github/workflows/deploy.yml` shows the additive line `+      environment: dev`. That single line silently changes the OIDC `sub` claim shape and is what the federated credential on the Entra app no longer matches.

## Recommended fix
**Do not revert the workflow.** Pinning the job to a GitHub environment is correct for FR-013 / Phase 1 guardrails — the fix belongs in Azure, not in this repo:

1. In the Azure portal → App registration `b2451691-200c-4d8d-b50f-a60396ddb606` (tenant `9b7cbd77-…`) → **Certificates & secrets → Federated credentials → Add credential**:
   - Issuer: `https://token.actions.githubusercontent.com`
   - Organization: `DevPost-Test-Hackathon`
   - Repository: `crosstown-app`
   - Entity type: **Environment**
   - Environment name: **`dev`**
   - Audience: `api://AzureADTokenExchange`
   - Subject (auto-generated): `repo:DevPost-Test-Hackathon/crosstown-app:environment:dev`
2. Save. No code change required. Retry by re-running run `25999139361` (`gh run rerun 25999139361`) or pushing a no-op commit.

Optional belt-and-suspenders if the environment in GitHub doesn't exist yet: confirm `Settings → Environments → dev` exists on the `DevPost-Test-Hackathon/crosstown-app` repo (the `environment: dev` line in the workflow implicitly requires it; if it's missing GitHub still issues the token but the env-protection rules don't apply — current failure mode rules this out, since the token was issued).

**Out of scope (do not touch):** `apps/judging/azure.yaml`, `infra/**`, any service Dockerfiles. None of them contribute to this failure.

---

## 2026-05-18 ~11:15 ET — Audio regression diagnosis: "Brooklyn → Ozone on the surface"

**Investigator:** Wanda (Maximoff)
**Report time:** 2026-05-18T11:14-11:15 ET (Sean, live orchestrator)
**Symptom:** Sean said "Brooklyn" → transcription received as "Ozone on the surface"

### Root cause classification: **B — Wrong/insufficient audio reached Foundry**

The orchestrator relay layer is committing audio buffers to Foundry prematurely or without adequate audio content. Two buffers were committed in the ~11:15 ET window. The second commit was **completely empty (0.00ms)**. The first commit had some audio but likely a very short/fragmented payload (Whisper hallucinated "Ozone on the surface" rather than "Brooklyn" — a classic short-audio hallucination pattern). This is not a Foundry/Whisper quality issue in isolation; the bad transcription is a downstream symptom of the relay sending insufficient audio.

### Direct log evidence

```
# Timestamp: 2026-05-18T15:15:14.878 UTC (= 11:15:14 ET)
{"TimeStamp": "2026-05-18T15:15:14.8786617+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=input_audio_buffer.committed"}
{"TimeStamp": "2026-05-18T15:15:14.8790645+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=conversation.item.added"}
{"TimeStamp": "2026-05-18T15:15:14.8790808+00:00", "Log": "15:15:14,878 voice.foundry INFO foundry.recv DROP type=conversation.item.done"}
{"TimeStamp": "2026-05-18T15:15:14.8807241+00:00", "Log": "15:15:14,880 voice.foundry INFO foundry.recv DROP type=response.created"}

# Response completes in <200ms — suspiciously fast, consistent with near-empty audio
{"TimeStamp": "2026-05-18T15:15:15.0601463+00:00", "Log": "15:15:15,059 voice.foundry INFO foundry.recv EMIT type=response.done -> Final"}

# Transcription deltas arrive (Foundry IS processing some audio from the first commit)
{"TimeStamp": "2026-05-18T15:15:15.3110530+00:00", "Log": "15:15:15,310 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.delta -> TranscriptDelta"}
# [5 more delta events through 15:15:15.328]

# *** SMOKING GUN ***
{"TimeStamp": "2026-05-18T15:15:15.434144+00:00", "Log": "15:15:15,433 voice.foundry ERROR foundry.recv ERROR event_id=event_DgtyVSvJslOzlEzUhcsVp code=input_audio_buffer_commit_empty type=invalid_request_error param=None message=Error committing input audio buffer: buffer too small. Expected at least 100ms of audio, but buffer only has 0.00ms of audio."}

# Transcription for the first (short) buffer completes — this is the "Ozone on the surface" result
{"TimeStamp": "2026-05-18T15:15:15.5710672+00:00", "Log": "15:15:15,570 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.completed -> TranscriptDelta"}
```

### Interpretation

| Fact | Implication |
|------|------------|
| `input_audio_buffer.committed` at 15:15:14 → transcription deltas fire | First buffer had SOME audio — mic is live and audio path is not completely broken |
| Second buffer committed at 15:15:15.434 with **0.00ms** | Relay called `input_audio_buffer.commit` on an empty buffer — no audio chunks were accumulated before commit |
| `response.done → Final` in <200ms after first commit | Response was trivially short; server-side VAD likely triggered on a very short audio segment |
| Wildly wrong transcription ("Ozone on the surface") | Whisper hallucination caused by receiving a very short, possibly near-silence audio clip — known Whisper behavior on <1s clips |

The relay layer is either: (a) committing the buffer too early (before mic audio accumulates), or (b) sending a `commit` without waiting for the frontend to stream sufficient `input_audio_buffer.append` chunks. The 0.00ms error confirms the orchestrator's relay called commit on an empty Foundry-side buffer at least once in this session.

### Recommended fix

**Stark:** In the orchestrator relay, add a minimum-audio-duration guard before committing the input audio buffer — do not call `input_audio_buffer.commit` unless the buffer holds ≥ 100ms of audio (matching Foundry's own enforced minimum). If the client sends a stop/commit signal with an empty buffer, drop the commit rather than forwarding it.

### Confidence: High

- The 0.00ms error is unambiguous and timestamped exactly in Sean's reported window (11:15 ET).
- No `voice.foundry ERROR` or relay errors on the audio path prior to this window → not a pre-existing crash.
- Transcription infrastructure (`gpt-4o-mini-transcribe`) is not at fault; it produced an output for the audio it received — the audio itself was the problem.
- Frontend microphone is live (audio DID reach the first buffer), so this is not Cause C (frontend capture broken).

---

## Risk if left unfixed
- **No code can reach the live Azure environment.** Every push to `main` fails before `azd provision` and `azd deploy` even start. Voice stack (`apps/orchestrator`, `apps/log_analyst`, `apps/frontend`) is frozen at whatever was last deployed — which, given there is **no successful run on record**, may mean nothing has *ever* deployed via this workflow and the live ACA apps are still on placeholder/quickstart images.
- **Hackathon impact (Track 2):** the Tuesday demo (specs/002-tuesday-demo) depends on the deploy lane producing a working `FRONTEND_URL` for the smoke test (`scripts/smoke-test.*` + `azure.yaml` postdeploy hook). With OIDC broken, the demo URL cannot be refreshed with current PR #21 / PR #22 / PR #27 changes (user-turn transcripts, VAD fix, service-advisor feature). Judges will hit stale or broken endpoints.
- **Eval/red-team live mode** (`EVAL_MODE=live ORCHESTRATOR_URL=…`) cannot be exercised against the deployed stack until this clears, so we lose live-path coverage on top of hermetic cassettes.
- **Time cost:** ~5 min Azure portal change once a Contributor on the app registration is available. Every hour of delay is an hour the Track 2 stack ships on stale bits.

---

## 2026-05-18 ~11:46 ET — Missing assistant response diagnosis

**Investigator:** Wanda (Maximoff)
**Report time:** 2026-05-18T11:46 ET (Sean, live orchestrator)
**Symptom:** Voice turn → tool fires (`get_disruption_status({"line": "L2"})`) → user sees tool-call panel + user transcripts — **no assistant message bubble appears.**

### Root cause classification: **B — Relay emits `Final(text="")` → frontend shows nothing**

The backend relay IS generating and forwarding a `Final` event after the tool call cycle. It is not dropped. However, the `Final` arrives with `text=""` because Foundry's cycle-2 response (post-tool-result) returned `response.done` with an **empty `output[]` array** (the server preempted cycle 2 before any text/audio was generated). The frontend's `final` case handler (`useVoiceSession.ts:242`) correctly falls through to the no-text branch: it clears `awaitingResponse: false` but adds **no assistant bubble**. Tool citations land in the `tool_result` frame but without a `final` with text there is no bubble for the answer.

### Direct log evidence

```
# Cycle 1 (healthy — first response, before the tool turn)
15:43:56,... voice.foundry INFO foundry.recv EMIT type=response.output_audio_transcript.delta -> TranscriptDelta  [×14]
15:43:56,... voice.foundry INFO foundry.recv EMIT type=response.output_audio.delta -> AudioDelta               [×12]
15:43:57,191 voice.foundry INFO foundry.recv EMIT type=response.output_audio_transcript.done -> TranscriptDelta
15:43:57,195 voice.foundry INFO foundry.recv EMIT type=response.done -> Final                ← HEALTHY

# Tool-call response (15:45:37–38) — correctly dropped
15:45:37,139 voice.foundry INFO foundry.recv DROP type=response.created
15:45:38,198 voice.foundry INFO foundry.recv EMIT type=response.function_call_arguments.done -> ToolCall  ← tool fires ✓
15:45:38,210 voice.foundry INFO foundry.recv DROP type=response.done            ← tool-call response correctly dropped

# Cycle 2 (post-tool) — SMOKING GUN
15:45:38,265 voice.foundry INFO foundry.recv DROP type=response.created
# ← ZERO response.output_audio_transcript.delta events in this window
# ← ZERO audio_delta events
15:45:38,576 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.completed -> TranscriptDelta  ← user msg 2 simultaneous
15:45:38,576 voice.foundry INFO foundry.recv EMIT type=response.done -> Final   ← 311ms cycle, empty output[]

# Cycle 3 (user msg 2 turn) — same empty pattern
15:45:56,627 voice.foundry INFO foundry.recv DROP type=response.created
15:45:57,069 voice.foundry INFO foundry.recv EMIT type=conversation.item.input_audio_transcription.completed -> TranscriptDelta
15:45:57,307 voice.foundry INFO foundry.recv EMIT type=response.done -> Final   ← also empty
```

### Interpretation

| Fact | Implication |
|------|-------------|
| Cycle 1 has 14 audio_transcript.delta events before response.done | Healthy Foundry voice response path works |
| Cycle 2 completes in **311 ms** with **zero** audio_transcript.delta events | Foundry returned empty response — no model output generated |
| `response.done → Final EMIT` fires at exact same ms as user msg 2 `transcription.completed` | Foundry server-VAD committed user msg 2 while cycle 2 was in flight; preempted cycle 2 |
| No relay-level `cancel_inflight` fired | Orchestrator did **not** proactively cancel — `response_in_flight` was `False` during tool-execution window |
| `_translate` (foundry_realtime.py:287): `not outputs` branch | `output=[]` → `Final(text="")` forwarded |
| `_handle_event` (orchestrator.py:391–403): `out_text=""` | `{"type":"final","text":"","citations":[...]}` sent to frontend |
| Frontend `useVoiceSession.ts:231`: `if (frame.text)` falsy → line 242 fallback | `awaitingResponse: false` — state cleared, **no assistant bubble created** |

### Root cause chain

```
User msg 1 voice turn
  → Foundry server-VAD auto-commits audio → cycle 1 response → tool call dispatched ✓
  → submit_tool_result() fires response.create for cycle 2
  → BUT: response_in_flight still False (set only on first assistant frame, NOT at submit_tool_result)
  → User msg 2 arrives; server-VAD auto-commits without orchestrator sending response.cancel
  → Foundry preempts cycle 2 → response.done with output=[] → Final(text="")
  → Frontend line 242 fallback → no bubble, awaitingResponse cleared
```

### Suspected commit

**PR #49** (`a92ecf3` — "fix(frontend): remove manual StopButton") is the proximate aggravator. Before PR #49, users could hit Stop → `cancel_response` → `_cancel_inflight(force=True)` — an explicit safety valve for mid-response barge-ins even when `response_in_flight` was False. Without the StopButton there is no compensating cancel path for the tool-result → cycle-2 window.

The **underlying gap** traces to PR #45/#46: `response_in_flight` is never set to `True` when `submit_tool_result()` fires `response.create` (orchestrator.py:334–376 — no `turn.response_in_flight = True` after that await). This gap existed since PR #45 but was masked by the StopButton.

**PR #53** (`fa20430`) is **not** the cause — it guards CLIENT-SIDE commits only; Foundry server-VAD commits bypass the guard.

### Recommended fix

**One line** in `apps/orchestrator/agent/orchestrator.py`, ToolCall branch of `_handle_event`, after `await session.submit_tool_result(ev.call_id, result)`:

```python
turn.response_in_flight = True  # cycle 2 response.create just fired via submit_tool_result
```

**Fix owner: Stark**

### Confidence: High

- Zero audio_transcript.delta events in cycle 2 is unambiguous — Foundry produced no output.
- 311ms cycle time is below any realistic model generation floor.
- `response_in_flight = False` gap confirmed by reading orchestrator.py:334–376.
- Frontend line 242 fallback for `frame.text=""` confirmed by reading useVoiceSession.ts:204–242.
- Tool citations delivered (`tool_result` frame) — tool path healthy; only answer bubble missing.

---

## 2026-05-18 ~13:56 ET — Resolution (PR #60 merged)

**Investigator:** Sean (segayle)
**Resolution time:** 2026-05-18T13:56 ET
**Root cause fix:** Disabled the relay-level auto-cancel in text/stop handlers

### What was fixed

PR #60 addresses the cycle-2 empty-response issue described above by removing the problematic `response.cancel` calls that were firing during tool-execution windows. The trade-off is explicit and acceptable: the assistant now **reliably replies after tool calls**; fast follow-up barge-ins may **briefly overlap** in audio output, but the modality contract is preserved (one user turn at a time, clean tool dispatch).

### The fix in detail

- **Removed:** relay-level auto-cancel on new user transcript frames during tool execution
- **Preserved:** explicit `response.cancel` path (future StopButton integration)
- **Result:** cycle-2 responses now generate reliably; voice loop end-to-end working

### Evidence

- Live frontend: https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ — voice input works, assistant reliably replies
- Judging app: https://mango-hill-0ee13cb0f.7.azurestaticapps.net/ — /api/teams now succeeds (cycle-2 generation fixed)
- Smoke test `/api/turn` passes with tool calls + citations + final assistant message

### Related PRs

- [PR #60](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/60) — fix(voice): disable PR #45 auto-cancel so AI reliably talks back
- [PR #57 (reverted)](https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/57) — attempted workaround via response deferral; revealed Foundry single-modality constraint

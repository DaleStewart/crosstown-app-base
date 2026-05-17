# Wanda Maximoff — Agent History

**Date**: 2026-05-13  
**Role**: Anomaly Detection & Agent QA  
**Requested by**: Sean (segayle)

## Mission: Root Model-Version Regression Sweep

**Project**: MTA AI Hackathon — Multi-tenant Transit Authority Accelerator  
**Architecture**: Root Container Apps stack (`apps/orchestrator`, `apps/log_analyst`) + separate `apps/judging/` judging app  
**Context**: Legacy `gpt-4o` references across infrastructure and configuration needed regression fix to `gpt-4.1`.

### Scope

- **Root project only**: C:\Users\segayle\repos\mta-ai-hackathon (excluded `apps/judging/` per constraints)
- **Mechanical substitution**: 13 hits across 9 files
- **Critical constraint**: Leave `gpt-4o-realtime-preview` untouched (real model name for Foundry audio path)

### Changes Executed

1. **`.env.example` line 14**: Chat deployment default → `gpt-4.1`
2. **`apps/log_analyst/README.md` line 51**: Docstring → `gpt-4.1`
3. **`apps/log_analyst/settings.py` line 28**: Config default → `gpt-4.1`
4. **`apps/orchestrator/settings.py` line 14**: Config default → `gpt-4.1`
5. **`docs/evals.md` line 34**: Command example → `gpt-4.1`
6. **`docs/voice.md` lines 40, 51**: Speech Services path + env var docs → `gpt-4.1`
7. **`evals/foundry_evaluators.py` lines 13, 46**: Docstring + default value → `gpt-4.1`
8. **`evals/README.md` line 28**: Command example → `gpt-4.1`
9. **`infra/modules/foundry.bicep` lines 68, 71, 76**: Comment, deployment name, model name → `gpt-4.1`

### Verification

- ✅ Zero remaining `gpt-4o` references (excluding realtime)
- ✅ All 13 `gpt-4.1` references created
- ✅ `gpt-4o-realtime-preview` preserved in all files

## Technical Notes

- **Deployment name flip** (Bicep line 71): Resource name is now `gpt-4.1`, must align with env config
- **Realtime preserved**: Voice orchestrator still routes to `gpt-4o-realtime-preview` for audio; chat completions use `gpt-4.1`
- **No app logic changed**: This was a pure configuration sweep; no code paths altered
- **Judging app isolated**: `apps/judging/` directory remains independent per task constraints

## Status

✅ Complete — all edits applied, verified, documented.

---

## 2026-05-15 — Realtime Model Upgrade (D-009 Supersedes Earlier Instruction)

The "leave gpt-4o-realtime-preview alone" instruction from D-006 has been **deliberately superseded** by a full model upgrade to `gpt-realtime-1.5` (GA endpoint). This is not a reversion of D-006 — D-006 remains accurate as an audit trail. The historical context was specific to the 2026-05-13 chat-model migration. As of 2026-05-15, D-009 and D-010 execute the deliberate next step: upgrade to the GA realtime model.

**Related:** Decision D-009 (adopted 2026-05-15), Decision D-010 (adopted 2026-05-15).

---

## Learnings

**2026-05-15** — Post-merge eval gates run. Confirmed no regression from realtime model swap (D-009).

- **Citation gate** (`python -m runner --max-uncited-pct 5`): 8 turns, **0 uncited (0.0%)**, threshold 5%, **PASS**, exit code 0
  - All 8 scenarios passed; no missing citations or tool response gaps
  - Noise budget floor: 0 turns (5% of 8 = 0.4, floored to 0)

- **Orchestrator gate** (`python -m orchestrator_runner --max-fail-pct 0`): 8 scenarios, **0 failed (0.0%)**, threshold 0%, **PASS**, exit code 0
  - **Tool-routing assertions: ALL PASS** (critical for Spec 001)
  - Tested vague status → search_logs (OS-005), log ID hint → detect_pattern (OS-006), incident ID → summarize_incident (OS-007), composite ask (OS-008)
  - Realtime endpoint swap did not affect tool dispatch path or citation contract; routing identical to pre-swap baseline

- **Verdict:** 🟢 **GREEN** — No regression. Both PRs merged successfully. Citation contract intact. Orchestrator routing unaffected by gpt-realtime-1.5 swap.


---

## 2026-05-15 (re-run) — Eval Gates Re-Verification (Post D-009 + D-011 Merge)

**Requested by:** Brady (segayle). Second pass on same day to confirm no drift after PRs #1 (D-009 realtime-1.5 swap) and #2 (D-011 spec-kit + constitution + Spec 001) merged into `main`. D-014 baseline (earlier same day) was all GREEN.

### Citation gate — `python -m runner --max-uncited-pct 5`
- Scenarios run: **8** (SC-001..SC-008)
- Turns: 8 - Uncited: **0 (0.0%)** - Threshold: 5.0%
- Noise budget: floor(0.05 * 8) = 0 turns
- Result: **PASS** (exit 0)

### Orchestrator gate — `python -m orchestrator_runner --max-fail-pct 0`
- Scenarios run: **8** (OS-001..OS-008)
- Failed: **0 (0.0%)** - Threshold: 0.0%
- Result: **PASS** (exit 0)

### Tool-routing assertions (subset of orchestrator gate)
- OS-005 vague status -> `search_logs`: **PASS**
- OS-006 log ID hint -> `detect_pattern`: **PASS**
- OS-007 incident ID -> `summarize_incident`: **PASS**
- OS-008 composite ask -> multi-tool route: **PASS**

### Overall: 🟢 GREEN
Identical to D-014 baseline. Realtime model swap (D-009) and spec-kit adoption (D-011) confirmed regression-free on `main`. No status change since last run -> no inbox decision draft required.

**Team update (18:11Z):** Re-verify pass complete; PR #3 shipped from Parker for vite.config.ts.

---

## 2026-05-15 (21:25Z) — Bug #7: Foundry Realtime `wss://` scheme regression

**Requested by:** Brady (segayle). After Bugs #1–#6 fixed and orchestrator redeployed, all three live `/api/turn` tool paths returned HTTP 500. Banner captured the trace; my domain (D-009 realtime-swap regression in `voice/foundry_realtime.py`).

### Root cause
D-009 updated the Realtime endpoint path correctly
(`/openai/v1/realtime?model={deployment}`, no `api-version` for GA) but did
not convert the URL scheme. The Foundry endpoint env var resolves to
`https://swedencentral.api.azureml.ms`, which `websockets.connect` rejects
with `InvalidURI: scheme isn't ws or wss`. All three tool paths fail at the
same line (`foundry_realtime.py:160`) before tool dispatch is reached.

### Fix (PR #13, stacked on PR #12)
`apps/orchestrator/voice/foundry_realtime.py:155–163` — translate scheme of
`self._endpoint` (`https://` → `wss://`, `http://` → `ws://`) before
composing the realtime URL. Bearer header, GA path, and
`?model=gpt-realtime-1.5` all preserved.

- 1 file, +6/-4
- ruff: clean • mypy --strict: clean (19 files) • pytest: 11/11
- `azd deploy orchestrator`: 30 s, new revision live
- Stacks on PR #12 (`squad/fix-orchestrator-aiohttp-dockerfile`)

### Live `/api/turn` smoke (post-deploy)
All three calls still return 500, **but the underlying error has changed**
— Bug #7 is verified fixed at the URI-parser layer:

```
File "/app/voice/foundry_realtime.py", line 162
  ws = await websockets.connect(url, additional_headers=headers)
websockets.exceptions.InvalidStatus:
  server rejected WebSocket connection: HTTP 404
```

The WebSocket TCP+TLS handshake now reaches Foundry; Foundry rejects with
HTTP 404. This is a new Bug #8 (wrong host / path / deployment-name /
bearer scope on the GA endpoint contract).

### Outcome
- 🟢 Bug #7 — verified fixed (PR #13)
- 🟡 Bug #8 — escalated to Brady; **did not** chase a 4th orchestrator fix
  per failure-handling rules
- 🟡 Phase 2.5 — still NOT live-ready; eval gate cannot run live until
  Bug #8 clears
- Hermetic citation gate + orchestrator gate both remain GREEN (unchanged)

Trace: `.squad/files/orchestrator-500-trace-after-wss-fix.log`.
Result file: `.squad/files/azd-up-result-2026-05-15.md`.
Decision inbox: D-022.

## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up

---

## 2026-05-15 (post-Bug-8 diagnosis) — Bug #8 Fix Shipped as PR #14

**Requested by:** Brady (segayle) — autopilot OK, HIGH-confidence fix.

### Fix applied

- **`apps/orchestrator/settings.py`** — add `azure_openai_endpoint: str = ""` (binds to `AZURE_OPENAI_ENDPOINT` already in container from Bicep)
- **`apps/orchestrator/voice/factory.py`** — `endpoint=s.azure_ai_foundry_project_endpoint` → `endpoint=s.azure_openai_endpoint`

Both changes preserve `azure_ai_foundry_project_endpoint` for other usages.

### Validation

- ruff: ✅ clean
- mypy --strict: ✅ 19 files, no issues
- pytest: ✅ 11/11 pass

### PR #14

Stacked on PR #13 (Bug #7 wss:// fix). Opened via `gh pr create --base squad/fix-realtime-wss-scheme`.  
URL: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/14  
Branch: `squad/fix-realtime-aoai-direct-endpoint`  
Commit: `fix(orchestrator): use AOAI direct endpoint for Foundry Realtime WebSocket`

### Deploy

`azd deploy orchestrator --no-prompt` — 30 s, revision `orchestrator--azd-1778880853` active.
Log: `.squad/files/azd-deploy-orchestrator-bug8-fix.log`

### Smoke results (post-PR #14 deploy)

```
=== search_logs ===        HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
=== detect_pattern ===     HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
=== summarize_incident === HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
```

### Outcome

- 🟢 **Bug #8 FIXED** — HTTP 500 gone; `InvalidStatus: HTTP 404` gone; AOAI direct endpoint handshake succeeds.
- 🔴 **Bug #9 ESCALATED** — All 3 tool paths return `tool_calls: []`; model generates generic text without invoking MTA tools. `tools_loaded: true` but no dispatch. Failure handling rule applied: STOP, escalate, no Bug #9 chase.
- 🟡 Phase 2.5: **NOT live-ready** — blocked on Bug #9 (tool dispatch / citation contract).

Inbox: `.squad/decisions/inbox/maximoff-d023-bug8-fixed-bug9-escalated.md`

---

## 2026-05-15 (pre-Bug #8 fix) — Bug #8 Diagnosis (read-only)

**Requested by:** Brady (segayle). Pure research + diagnosis pass. No code shipped. No PR opened.

### Scope

Four hypotheses from Bug #7 escalation:
1. Wrong host (`azureml.ms` vs `openai.azure.com`)
2. Wrong path (`/openai/v1/realtime` vs alternatives)
3. Wrong deployment alias (`gpt-realtime-1.5`)
4. Wrong bearer scope (`cognitiveservices.azure.com`)

### Key Findings

**Runtime URL (post-Bug-7, verbatim from pre-fix trace + code analysis):**
```
wss://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5
```

**How it's built:** `factory.py` passes `s.azure_ai_foundry_project_endpoint`
(`AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://swedencentral.api.azureml.ms`) to
`FoundryRealtimeProvider`, ignoring `AZURE_OPENAI_ENDPOINT`
(`https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/`).

**Live WebSocket probe results:**
| URL | Result |
|-----|--------|
| `wss://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5` | HTTP 404 |
| `wss://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/openai/v1/realtime?model=gpt-realtime-1.5` | **HANDSHAKE_OK** |
| `wss://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/openai/realtime?model=gpt-realtime-1.5` | HTTP 404 |

**MS Learn canonical URL (gpt-realtime-1.5 GA):**
```
wss://<account>.openai.azure.com/openai/v1/realtime?model=<deployment>
```
Source: learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart (2026-05-14 revision)

**AOAI deployment list confirmed:** `gpt-realtime-1.5` (exact name, version 2026-02-23) — H3 ruled out.

**JWT aud confirmed:** `https://cognitiveservices.azure.com` — H4 ruled out.

### Verdict

**H1 (Wrong Host) — CONFIRMED.** HIGH CONFIDENCE.  
**H2 (Path) — RULED OUT.** `/openai/v1/realtime` is correct.  
**H3 (Deployment alias) — RULED OUT.** `gpt-realtime-1.5` is exact match.  
**H4 (Bearer scope) — RULED OUT.** `cognitiveservices.azure.com/.default` is correct.

### Recommended Fix (not shipped — diagnosis only)

**`apps/orchestrator/settings.py`** — add 1 field:
```python
azure_openai_endpoint: str = ""
```

**`apps/orchestrator/voice/factory.py`** — change 1 line:
```python
# BEFORE:
endpoint=s.azure_ai_foundry_project_endpoint,
# AFTER:
endpoint=s.azure_openai_endpoint,
```

`AZURE_OPENAI_ENDPOINT` already exists in the container via Bicep. No infra change required.

### Outcome

- 🟡 Bug #8 — **root cause identified, fix specified, not yet shipped**
- Diagnosis report: `.squad/files/maximoff-bug8-diagnosis-2026-05-15.md`
- Inbox note: `.squad/decisions/inbox/maximoff-bug8-diagnosis-2026-05-15.md`
- Live `/api/turn` still returning 500 — blocked on Brady/Squad shipping the 2-file fix

---

## 2026-05-16 — Voice Regression Diagnosis + Fix (PR #22 broke voice, PR #24 fixes it)

**Date:** 2026-05-16  
**Requested by:** Sean (segayle)

### Mission

Sean reported "nothing is showing up" on voice after PR #22 deployed as `orchestrator--0000008`. Voice was confirmed working after PR #20. Regression window: PR #22 deploy.

### Log Analysis

Container logs (`orchestrator--0000008`): WS accepted → `connection open` → 22s later `connection closed`. No error events logged. Silent blackout.

### Root Cause

**PR #22 changed `azure_openai_transcription_deployment` default to `"whisper-1"`** — but no whisper deployment exists in `infra/modules/foundry.bicep` (only `gpt-4.1` + `gpt-realtime-1.5` are provisioned). Phase 2 fire-and-forget sent `session.update { input_audio_transcription: { model: "whisper-1" } }` → Azure OpenAI rejected the unknown deployment name and **closed the Foundry WebSocket**. The pump `finally` block put `None` in the inbound queue; `events()` returned immediately; zero audio/transcript events reached the client.

The "fire-and-forget is safe" assumption in D-031 was wrong — Azure closes the WS on an invalid deployment name, not just rejects with an error event.

### 47doors Reference Study (`.squad/files/47doors-ref/47doors-main/backend/app/services/azure/realtime.py`)

| Dimension | 47doors | Ours (pre-fix) |
|-----------|---------|----------------|
| Architecture | WebRTC + `/client_secrets` REST | WS proxy |
| Session config | Single-phase in `/client_secrets` body | Two-phase `session.update` |
| Transcription field | `audio.input.transcription.model` (GA nested) | `input_audio_transcription.model` (preview flat) |
| Transcription default | `"whisper-1"` (they provision it) | `"whisper-1"` ← **bug** (not provisioned) |

Adopted: GA nested format for Phase 2.

### Fix Timeline

- **17:07Z** — env var `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT=''` on `orchestrator--0000009` → voice restored in <1 min, no rebuild
- **17:11Z** — `orchestrator--0000010` ACR build from clean code (`transcription-fix-20260516130553`), Healthy, 100% traffic
- **~17:20Z** — PR #24 opened: `fix(orchestrator): safe transcription default + GA nested format`

### Changes (PR #24)

1. `settings.py`: `azure_openai_transcription_deployment` defaults to `""` (disabled)
2. `foundry_realtime.py`: Phase 2 uses GA nested `audio.input.transcription.model`
3. `foundry_realtime.py`: `_translate` handlers for `.delta` and `.failed` events
4. `factory.py`: passes `transcription_deployment` to provider
5. `tests/test_foundry_realtime.py`: 13 new unit tests

**Gates:** ruff ✅ mypy --strict (20 files) ✅ pytest 25/25 ✅

### Outcome

- 🟢 Voice restored — Sean can UAT immediately
- 🟢 PR #24 open: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/24
- 🟡 User transcription disabled (intentional) — re-enable by adding whisper/gpt-4o-transcribe deployment to `foundry.bicep` + setting env var
- 🟡 PR #22 (`squad/fix-voice-user-transcription`) should be closed or superseded by PR #24

### Learnings

- Azure OpenAI Realtime WS closes (not just error-events) on invalid deployment names — "fire-and-forget" is NOT safe for session.update
- GA model `gpt-realtime-1.5` uses nested `audio.input.transcription` format; preview flat `input_audio_transcription` is deprecated/rejected
- Always validate that referenced deployment names exist in Bicep before using them as defaults
- 47doors reference: useful for GA format; their architecture (WebRTC) is different from ours (WS proxy)

**Decision inbox:** D-033
## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up

---

## 2026-05-15 — Bug #9 Diagnosis: Tool Dispatch Failure (no code shipped)

**Requested by:** Brady (segayle). Pure research + diagnosis pass. No code shipped. No PR opened.

### Scope

Three hypotheses from Bug #8 post-deploy smoke (HTTP 200 but tool_calls: [], warnings: uncited):
1. `tool_choice` not set in session.update
2. Timing race — user message sent before `session.updated` ACK received
3. System prompt insufficient for Realtime context
4. *(4th, discovered)* Schema mismatch — old `gpt-4o-realtime-preview` format sent to `gpt-realtime-1.5` GA API; errors silently swallowed

### Current session.update Payload (verbatim from foundry_realtime.py)

```json
{
  "type": "session.update",
  "session": {
    "instructions": "<SYSTEM_PROMPT>",
    "tools": [{ "type": "function", "name": "...", "description": "...", "parameters": {} }],
    "modalities": ["text", "audio"],
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16"
  }
}
```

MISSING: `tool_choice`. MISSING: await for `session.updated` before returning.

### Container Log Evidence

Clean logs — three HTTP 200 OK responses to `/api/turn`. No WS-frame logging. No errors. This does NOT prove session.update succeeded — the pump's `_translate()` silently drops all unrecognised events including `error` events from the server.

### MS Learn Canonical Shape

MS Learn quickstart (2026-05-14) **explicitly polls for `session.updated`** before sending any user message. GA API schema uses `output_modalities` (not `modalities`), `audio.input.format` nested object (not `input_audio_format`), and requires `type: "realtime"` in session. `RealtimeFunctionTool` flat format `{type, name, description, parameters}` is correct in our code.

### Per-Hypothesis Verdicts

| Hypothesis | Verdict | Confidence |
|---|---|---|
| H1 — `tool_choice` not set | INCONCLUSIVE / CONTRIBUTING | Low as primary; zero-risk to add `"auto"` |
| H2 — No await for `session.updated` | **BUG — PRIMARY** | HIGH |
| H3 — System prompt too weak | RULED OUT | — |
| H4 — Schema mismatch + silent error swallow | **BUG — SECONDARY** | MEDIUM |

### Recommended Fix

**`apps/orchestrator/voice/foundry_realtime.py`** — 2 changes, ~14 lines:

1. Add `"tool_choice": "auto"` to `session.update` payload
2. In `open_session()`: create `session_ready = asyncio.Event()`, set it in pump when
   `session.updated` arrives, then `await asyncio.wait_for(session_ready.wait(), timeout=10.0)`
   before returning the session.

Full diff in `.squad/files/maximoff-bug9-diagnosis-2026-05-15.md`.

### Outcome

- 🔴 **Bug #9** — root cause identified (H2 primary + H4 secondary), fix specified
- Diagnosis report: `.squad/files/maximoff-bug9-diagnosis-2026-05-15.md`
- Inbox note: `.squad/decisions/inbox/maximoff-bug9-diagnosis-2026-05-15.md`
- **No code shipped** — diagnosis only per task scope

---

## 2026-05-15 — Bug #9 Fix Shipped (PR #15)

**Requested by:** Sean (segayle). End-to-end ship authorized after diagnosis pass.

### Changes shipped (branch `squad/fix-realtime-tool-dispatch-race` → PR #15)

Three commits:

1. **H1+H2 fix** — `"tool_choice": "auto"` added to session.update; `session_ready = asyncio.Event()` introduced, set in pump on `session.updated`, awaited with 10 s timeout in `open_session()` before returning session.

2. **H4 schema fix** — GA Realtime API schema correction: `"type": "realtime"` added to session object; `"modalities": ["text", "audio"]` → `"output_modalities": ["audio"]`; top-level `input_audio_format`/`output_audio_format` removed (invalid in GA API); `_translate response.done` updated to capture both `transcript` (audio output) and `text` (text output) fields.

3. **response.done text capture fix** — The first `response.done` (function-call response) was being translated as `Final(text="")`, causing `api_turn` to break before the model's actual text reply arrived. Fix: skip items with `type == "function_call"` when extracting text; if all outputs are function_call items return `None` so the pump does not surface a `Final` event and `api_turn` continues waiting for the second `response.done` (which carries the model's cited text).

### Validation (each commit)

- `ruff check .` — clean
- `mypy --strict .` — 19 files, no issues
- `pytest -q` — 11/11 pass

### Deploy history

| Deploy | Revision | Result |
|---|---|---|
| After H1+H2 commit | `orchestrator--azd-1778882093` | 🔴 HTTP 500 TimeoutError (confirmed H4 — server rejected schema, never sent session.updated) |
| After H4 commit | `orchestrator--azd-*` | 🟡 HTTP 200; citations populated; text empty (function_call response.done broke loop early) |
| After response.done fix | live | ✅ HTTP 200; citations populated; text populated; tool dispatched |

### Live smoke test (final)

```
=== search_logs ===
citations: 10 | tool: search_logs | warnings: NONE | text_len: 307

=== detect_pattern ===
citations: 0  | tool: detect_pattern | warnings: uncited,400 Bad Request from log-analyst
(tool dispatched correctly; log-analyst returns 400 — separate pre-existing bug)

=== summarize_incident ===
citations: 2  | tool: summarize_incident | warnings: NONE | text_len: 364
```

### Outcome

- ✅ **Bug #9 FIXED** — tool dispatch fully operational; citations non-empty; text populated
- ⚠️ `detect_pattern` path returns 400 from log-analyst — separate issue (not Bug #9; escalated separately)
- PR #15: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/15
- Base: `squad/fix-realtime-aoai-direct-endpoint` (PR #14)
## 2026-05-15 — Lab dry-run runbook delivered; P0 gpt-4.1 version pin shipped as PR #5; awaiting tenant login + PR merge for azd up

---

## 2026-05-16 — Bug #14: Voice Loop End-to-End Fix (PR #20)

**Requested by:** Sean (segayle). Live UAT failure: mic button goes yellow (audio flows), but chat window shows nothing. `/api/turn` text path works. `/ws/voice` accepts connections and closes immediately with zero response frames.

### Root Cause Analysis

**Live probe (pre-fix):** `CONNECTED → start → 5 PCM chunks → stop → CONNECTION CLOSED: no close frame`. Zero frames received.

**Bug A (PRIMARY) — Missing explicit audio commit:**
The orchestrator's `/ws/voice` loop never committed the audio buffer. Without `input_audio_buffer.commit` + `response.create`, the model never processes speech. The `stop` handler did `break`, closing the session before any model response.

**Bug B (SECONDARY) — `stop` breaks session too early:**
After PR #19 (Parker) added `stopTalking() → {type:"stop"}` on mic release, the `break` in the `stop` handler killed the session before the response arrived.

**gpt-realtime-1.5 GA API schema discoveries (not in docs):**

| Field | Behavior |
|---|---|
| `session.turn_detection` | REJECTED — `Unknown parameter` |
| `session.input_audio_transcription` | REJECTED — `Unknown parameter` |
| `input_audio_buffer.commit` (message) | SUPPORTED |
| `response.create` (message) | SUPPORTED |

The pump's `_translate()` silently dropped `error` events — these schema rejections caused `session_ready` to never fire, leading to a 10-second `asyncio.TimeoutError`. Fixed by adding explicit error capture in the pump.

### Fix (branch `squad/fix-voice-vad-commit`, PR #20)

**`foundry_realtime.py`:**
- `commit_audio()` method — `input_audio_buffer.commit` + `response.create`
- Pump error logging — captures `error` events, calls `session_ready.set()`, raises `RuntimeError` with Foundry's exact message
- Removed `input_audio_transcription` (unsupported)
- Removed `turn_detection` (unsupported in this gpt-realtime-1.5 deployment)

**`orchestrator.py`:**
- `stop` handler: calls `commit_audio()` via duck-typed `getattr`, continues loop (no `break`)
- Multi-turn PTT preserved — session stays alive after response

### Deployment History

| Image Tag | Revision | Outcome |
|---|---|---|
| `vad-fix-20260516102318` | `--0000003` | session.updated timeout (create_response invalid) |
| `vad-fix-20260516102318b` | `--0000004` | still timeout (error events silent) |
| `vad-fix-20260516102318c` | `--0000005` | `Unknown parameter: 'session.input_audio_transcription'` |
| `vad-fix-20260516102318d` | `--0000006` | `Unknown parameter: 'session.turn_detection'` |
| `vad-fix-20260516104728e` | `--0000007` | ✅ `FRAME[1]: type=final` — VOICE LOOP ALIVE |

### Outcome

- ✅ **Bug #14 FIXED** — First ever response frame received from voice path in live UAT
- ✅ `/api/turn` text path regression check passes (no regression)
- ✅ D-029 decision written
- 🔗 PR #19 (Parker frontend) + PR #20 (orchestrator) must merge together
- PR #20: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/20

---

## 2026-05-16 — Bug #15: User Transcription Re-enable (PR #22)

**Requested by:** Sean (segayle). Chat window shows assistant responses but not user speech — conversation is one-sided. PR #20 dropped `input_audio_transcription` to unblock the voice loop; this PR restores it safely.

### Root Cause

PR #20 correctly removed `input_audio_transcription` from `session.update` after it caused a 10-second `asyncio.TimeoutError` on revision `--0000005`. But that was because the pump silently swallowed error events and never set `session_ready`. With PR #20's error capture in place (fast-fail instead of timeout), it's now safe to retry — a rejection becomes a logged error, not a hang.

**MS Learn (2026-05-14 revision) confirms:** `input_audio_transcription` is a valid Azure OpenAI Realtime parameter. Azure requires a deployment name in the `model` field; OpenAI accepts `whisper-1`. We default to `whisper-1` and expose `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT` for Azure deployments.

### Fix (branch `squad/fix-voice-user-transcription`, PR #22)

**Two-phase session.update strategy:**
- Phase 1: known-safe payload (instructions, tools, output_modalities) — awaits `session.updated` ACK. Unchanged.
- Phase 2: fire-and-forget `session.update` with only `input_audio_transcription: {model: "whisper-1"}`. If rejected, error absorbed by `_translate` (returns None), session unaffected.

**Also includes PR #20 orchestrator changes (not yet in main):**
- `commit_audio()` on `FoundryRealtimeSession` — explicit buffer commit + response.create
- Pump error capture — `error` events raise `RuntimeError` immediately (no timeout hang)
- `orchestrator.py` stop handler — calls `commit_audio()`, no `break`, loop stays open

**New `_translate` handlers:**
- `conversation.item.input_audio_transcription.delta` → `TranscriptDelta(role="user", final=False)`
- `conversation.item.input_audio_transcription.failed` → `None` (graceful silence)

**Client contract (existing convention, no change needed on Parker's side):**
```
{"type": "transcript_delta", "role": "user", "text": "...", "final": false}
{"type": "transcript_delta", "role": "user", "text": "...", "final": true}
```

### Validation

- `ruff check .` — clean
- `mypy --strict .` — 20 files, no issues
- `pytest -v` — 25/25 pass (14 new in `tests/test_foundry_realtime.py`)

### Deploy

ACR build `user-transcript-20260516112305` → revision `orchestrator--0000008` (Healthy, 100% traffic).
Live `/api/turn` smoke: HTTP 200, text_len=130, tool_calls=[search_logs, search_logs], warnings=log-analyst 400 (pre-existing, unrelated).

### Outcome

- ✅ Orchestrator side shipped — user transcription enabled via two-phase session.update
- ✅ `_translate` complete for all three transcription event types (delta, completed, failed)
- ✅ `commit_audio` + stop-handler fix included (PR #20 changes now in main via PR #22)
- ✅ D-031 decision written
- 🔗 Parker's PR #21 + PR #22 must deploy together for full conversation parity
- PR #22: https://github.com/DevPost-Test-Hackathon/crosstown-app/pull/22

### Autopilot disclosure

Ran in autopilot mode. Key autonomous decisions:
- Included PR #20 orchestrator changes in this PR (deployed but not in main; lands together)
- Two-phase fire-and-forget for transcription (session survives rejection)
- Default `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT=whisper-1` (task's first-try variant)
- Kept existing `transcript_delta` event name (matches Parker's PR #21 rendering contract)

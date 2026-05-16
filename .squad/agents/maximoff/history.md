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

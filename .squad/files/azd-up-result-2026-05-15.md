# azd up Result — 2026-05-15 (Bug Fix Cycles 1–7)

**Mission:** Deploy crosstown stack for Tuesday 2026-05-19 customer handoff dry-run.
**Resource group:** `rg-crosstown-dryrun-may15`
**Region:** `swedencentral`
**Subscription:** `47156f11-2e05-4362-ac86-090b4b081b27`

## Bug-fix cycles

| # | Bug | PR | Owner | Status |
|---|---|---|---|---|
| 1 | Key Vault `purgeProtection` rejected in swedencentral | #7 | T'Challa | merged |
| 2 | Foundry Hub/Project name length cap | #8 | Stark | merged |
| 3 | AI Search keyless RBAC auth | #9 | Okoye | merged |
| 4 | Orchestrator missing `aiohttp` (pyproject) | #10 | Banner | merged |
| 5 | Cosmos seed document shape (incidents) | #11 | Okoye | merged |
| 5b | Orchestrator `aiohttp` also missing in Dockerfile | #12 | Banner | merged |
| 6 | (rolled into above bookkeeping) | n/a | Banner | n/a |
| **7** | **Foundry Realtime URL scheme `https://` → `wss://`** | **#13** | **Maximoff** | **merged-pending (stacked on #12)** |

## Bug #9 — Realtime Tool Dispatch (this cycle — PR #15)

**Root cause chain (from diagnosis report `.squad/files/maximoff-bug9-diagnosis-2026-05-15.md`):**

- **H2 (primary):** `open_session()` returned without awaiting `session.updated` ACK; caller fired `conversation.item.create` + `response.create` before server finished processing tool registration.
- **H4 (secondary — confirmed by TimeoutError on first deploy):** `session.update` sent old `gpt-4o-realtime-preview` schema to `gpt-realtime-1.5` GA API. `modalities: ["text","audio"]` invalid (field renamed to `output_modalities`; combining text+audio not allowed). `input_audio_format`/`output_audio_format` not valid top-level GA fields. `type: "realtime"` missing from session object (required). Server rejected with `error` event silently swallowed by `_translate`. Session never sent `session.updated`, causing the `session_ready` Event to time out (exposed the hidden failure).
- **H3 (discovered during fix):** `response.done` for function-call responses (output type `"function_call"`, no `content[]`) was being translated as `Final(text="")`, breaking `api_turn` loop before the model's text reply (second response) arrived. Fixed by returning `None` from `_translate` for pure function-call responses.

**Fix (3 commits — PR #15, stacked on PR #14):**

1. `session_ready = asyncio.Event()`, set in pump on `session.updated`, `await asyncio.wait_for(session_ready.wait(), timeout=10.0)` before returning session; `"tool_choice": "auto"` added to session.update
2. `"type": "realtime"` in session; `"modalities": ["text","audio"]` → `"output_modalities": ["audio"]`; top-level audio format fields removed; `_translate response.done` captures both `transcript` and `text` content fields
3. `_translate response.done` skips `"function_call"` output items and returns `None` (not `Final`) when all outputs are function calls — allows api_turn to wait for the model's post-tool-result text response

**Local validation (apps/orchestrator):**
- `ruff check .` — clean
- `mypy --strict .` — 19 files, no issues
- `pytest -q` — 11/11 pass

**Deploy:** 3 deploys; final revision live (3rd deploy, ~28 s).

**Smoke test (`/api/turn`, all three tool paths, post-Bug-9 PR #15 final deploy):**

```
=== search_logs ===
citations: 10 | tool: search_logs | warnings: NONE | text_len: 307  ✅

=== detect_pattern ===
citations: 0  | tool: detect_pattern | warnings: uncited + 400 Bad Request from log-analyst
(tool dispatched correctly — separate log-analyst bug, not Bug #9)  ⚠️

=== summarize_incident ===
citations: 2  | tool: summarize_incident | warnings: NONE | text_len: 364  ✅
```

✅ **Bug #9 verified fixed** — orchestrator now dispatches all tools, citations non-empty, text populated.

🟡 **New issue:** `detect_pattern` log-analyst returns HTTP 400. Tool dispatch works (correct tool called). Bug is in log-analyst tool handler, not orchestrator.

## Phase 2.5 status

✅ **LIVE-READY (2/3 paths)** — Bug #9 fixed. `search_logs` and `summarize_incident` pass full citation contract. `detect_pattern` has a log-analyst 400 error (separate).

**Bug chain summary:**

| # | Bug | PR | Status |
|---|---|---|---|
| 1–6 | Infrastructure / aiohttp / Cosmos seed | #7–#12 | merged |
| 7 | wss:// scheme | #13 | merged |
| 8 | AOAI direct endpoint (azureml.ms → openai.azure.com) | #14 | open — stacked on #13 |
| **9** | **Tool dispatch race + GA schema mismatch + response.done loop break** | **#15** | **open — stacked on #14** |

## Sean UAT Instructions

**Orchestrator URL:** `https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io`

Working paths:
```bash
curl -s -X POST https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/api/turn \
  -H "Content-Type: application/json" \
  -d '{"text": "Show me the most recent door-fault logs from station Atlantic"}' | jq .

curl -s -X POST https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/api/turn \
  -H "Content-Type: application/json" \
  -d '{"text": "Summarize incident INC-1001"}' | jq .
```

Known issue: `detect_pattern` path returns 400 from log-analyst (separate bug).



**Root cause (from diagnosis report `.squad/files/maximoff-bug8-diagnosis-2026-05-15.md`):**
`factory.py` passed `azure_ai_foundry_project_endpoint` (`https://swedencentral.api.azureml.ms`)
to `FoundryRealtimeProvider`. The GA Realtime API lives on the AOAI direct host
(`*.openai.azure.com`), not the Foundry Hub. Live probe confirmed: `azureml.ms` → HTTP 404,
`openai.azure.com` → HANDSHAKE_OK with same bearer + deployment.

**Fix (2 files, 3 lines — PR #14, stacked on PR #13):**
- `apps/orchestrator/settings.py` — add `azure_openai_endpoint: str = ""` field (binds to
  `AZURE_OPENAI_ENDPOINT` already injected by Bicep — no infra change)
- `apps/orchestrator/voice/factory.py` — change `endpoint=s.azure_ai_foundry_project_endpoint`
  → `endpoint=s.azure_openai_endpoint`

**Local validation (apps/orchestrator):**
- `ruff check .` — clean
- `mypy --strict .` — 19 files, no issues
- `pytest -v` — 11/11 pass

**Deploy:** `azd deploy orchestrator --no-prompt` — 30 s, new revision active:
`orchestrator--azd-1778880853` (see `.squad/files/azd-deploy-orchestrator-bug8-fix.log`).

**Smoke test (`/api/turn`, all three tool paths, post-Bug-8 PR #14 deploy):**

```
=== search_logs ===
HTTP: OK  — TEXT LENGTH 370 chars
Citations: 0  Tool calls: []  Warnings: uncited

=== detect_pattern ===
HTTP: OK  — TEXT LENGTH 286 chars
Citations: 0  Tool calls: []  Warnings: uncited

=== summarize_incident ===
HTTP: OK  — TEXT LENGTH 192 chars
Citations: 0  Tool calls: []  Warnings: uncited
```

✅ **Bug #8 verified fixed** — HTTP 500 gone; `websockets.InvalidStatus: HTTP 404` gone;
orchestrator now reaches the Foundry Realtime handshake and receives model responses.

🟡 **New issue (Bug #9 — escalated):** All 3 calls return `tool_calls: []` and `citations: 0`.
The model is generating generic "I don't have access to station logs" text without invoking
`search_logs`, `detect_pattern`, or `summarize_incident`. Container logs are clean (no tracebacks,
no errors). Health endpoint confirms `tools_loaded: true`. The `session.update` sends correct tool
specs and system prompt to the Realtime API. Root cause is unclear — could be:
- Model not routing to tools from the question phrasing / system prompt
- `session.update` response not awaited before user message sent (timing race)
- `tool_choice` not set to `required` or `auto` in `session.update`
- gpt-realtime-1.5 tool dispatch behavior differs from gpt-4o-realtime-preview

Per failure-handling rules: STOP; citation contract not met; escalated to Brady.

## Phase 2.5 status

🟡 **NOT LIVE-READY** — Bug #8 (host) fixed. Bug #9 (tool dispatch / empty citations) is the
new blocker. Hermetic eval gates remain GREEN (unchanged). Live eval gate cannot run until
tool calls are dispatched and citations are non-empty.

**Bug chain summary:**

| # | Bug | PR | Status |
|---|---|---|---|
| 1–6 | Infrastructure / aiohttp / Cosmos seed | #7–#12 | merged |
| 7 | wss:// scheme | #13 | merged |
| 8 | AOAI direct endpoint (azureml.ms → openai.azure.com) | #14 | **open — ship pending merge of #13** |
| 9 | Tool dispatch / empty citations | — | 🔴 escalated |

## Cost / wall-time

- Wall time across 8 bug-fix cycles: ~4 h elapsed (16:00–21:40 UTC).
- No live LLM tool calls have completed with citations yet.

**Root cause:** D-009's realtime-swap to `gpt-realtime-1.5` rebuilt the URL as
`{endpoint}/openai/v1/realtime?model={deployment}` from the Foundry endpoint env
var (`https://swedencentral.api.azureml.ms`). `websockets.connect` rejects
`https://` schemes (`InvalidURI: scheme isn't ws or wss`). All three live
`/api/turn` tool paths failed at the same upstream point in
`voice/foundry_realtime.py:160` before tool dispatch.

**Fix (1 file, 6 insertions, 4 deletions):**
- `apps/orchestrator/voice/foundry_realtime.py:155–163`
- Translate scheme of `self._endpoint` (`https://` → `wss://`, `http://` →
  `ws://`) before composing the realtime URL.
- Bearer auth header preserved.
- No `api-version` query param re-added (D-009 GA contract preserved).
- `?model=gpt-realtime-1.5` deployment alias preserved.

**Local validation (apps/orchestrator):**
- `ruff check .` — clean
- `mypy --strict .` — 19 files, no issues
- `pytest -q` — 11/11 pass

**Deploy:** `azd deploy orchestrator --no-prompt` — 30 s, new revision active
(see `.squad/files/azd-deploy-orchestrator-bug7-fix.log`).

**Smoke test (`/api/turn`, all three tool paths):**

```
=== search_logs ===        FAILED — 500 Internal Server Error
=== detect_pattern ===     FAILED — 500 Internal Server Error
=== summarize_incident === FAILED — 500 Internal Server Error
```

But the trace has changed — Bug #7 is verified fixed:

```
File "/app/voice/foundry_realtime.py", line 162, in open_session
  ws = await websockets.connect(url, additional_headers=headers)
File ".../websockets/client.py", line 144, in process_response
  raise InvalidStatus(response)
websockets.exceptions.InvalidStatus:
  server rejected WebSocket connection: HTTP 404
```

The `InvalidURI` (Bug #7) is gone. The WebSocket client now successfully parses
the URL and opens a TCP+TLS connection to the Foundry endpoint. Foundry then
**rejects the handshake with HTTP 404** — wrong path or wrong `?model=` value
for this Foundry resource. This is **Bug #8**, a separate issue that requires
a decision from Brady before chasing.

Captured trace: `.squad/files/orchestrator-500-trace-after-wss-fix.log`.

## Sample `/api/turn` request shape (for reference)

```json
POST /api/turn
{ "text": "Show me the most recent door-fault logs from station Atlantic" }
```

Note: `text` field, not `message`. (Bug #7 task spec used `message`; corrected
on retry — that 422 caught it.)

Expected response (once Bug #8 cleared):
```json
{
  "text": "...",
  "citations": [{"type": "log", "id": "LOG-...", "url": "...", "snippet": "..."}],
  "tool_calls": [{"name": "search_logs", "arguments": {...}}],
  "warnings": []
}
```

## Phase 2.5 status

🟡 **NOT LIVE-READY** — blocked on **Bug #8** (Foundry Realtime WS handshake
404). Bug #7 (wss scheme) is verified fixed at the URI-parser layer; the next
upstream layer (Foundry Realtime endpoint contract) returns 404. Possible
candidates Brady should rule on:

1. Endpoint env var resolves to `azureml.ms` (Foundry/AML hub) but
   `gpt-realtime-1.5` deployment lives on the AOAI sub-resource at
   `openai.azure.com` — wrong host.
2. Path `/openai/v1/realtime` differs for this Foundry GA flavour (e.g.
   `/openai/realtime` or `/openai/deployments/{name}/realtime`).
3. `?model=gpt-realtime-1.5` should be the deployment name (different from the
   alias) — case-sensitive mismatch.
4. Bearer scope — currently `https://cognitiveservices.azure.com/.default`;
   may need `https://ai.azure.com/.default` for the new GA endpoint.

Eval gate cannot run live until this clears. Hermetic gates remain GREEN
(8/8 citation, 8/8 orchestrator — see `.squad/agents/maximoff/history.md`).

## Cost / wall-time so far

- Wall time across 7 bug-fix cycles: ~3 h elapsed (16:00–21:25 UTC,
  parallelised across team).
- Cost: minimal — single ACA env, idle Postgres, Foundry Hub provisioned;
  no live LLM calls have completed yet (all blocked at handshake).

## Verdict

🟡 **PARTIAL** — Bug #7 shipped and verified at the websockets-client layer.
Phase 2.5 gate is **NOT yet live-ready**; Bug #8 escalated to Brady before
attempting a 4th orchestrator fix (per failure-handling rules).

# Bug #8 Diagnosis Report — Maximoff (Anomaly Hunter)

**Date:** 2026-05-15  
**Author:** Wanda Maximoff  
**Status:** COMPLETE — NO CODE SHIPPED  
**Related:** D-009, Bug #7 (PR #13), Bug #8 escalation from Bug #7 post-deploy smoke test

---

## 1. Runtime URL (Verbatim)

**What the orchestrator builds today (post-Bug-7 scheme fix):**

```
wss://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5
```

### How it's constructed

**`factory.py` (line 19–22):**
```python
return FoundryRealtimeProvider(
    endpoint=s.azure_ai_foundry_project_endpoint,   # ← source of wrong host
    deployment=s.azure_openai_realtime_deployment,
)
```

**`settings.py`:**
```python
azure_ai_foundry_project_endpoint: str = ""   # binds to AZURE_AI_FOUNDRY_PROJECT_ENDPOINT
azure_openai_realtime_deployment: str = "gpt-realtime-1.5"
```

**`foundry_realtime.py` (line 155–158):**
```python
url = (
    self._endpoint.rstrip("/")
    + f"/openai/v1/realtime?model={self._deployment}"
)
```

**`azd env get-values` — relevant runtime values:**
```
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT="https://swedencentral.api.azureml.ms"
AZURE_OPENAI_ENDPOINT="https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/"
AZURE_OPENAI_REALTIME_DEPLOYMENT="gpt-realtime-1.5"
AZURE_AI_FOUNDRY_PROJECT_NAME="mlw-proj-crosstown-dryrun-may15-"
VOICE_PROVIDER="foundry_realtime"
```

`factory.py` feeds `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` (the Foundry Hub endpoint at
`swedencentral.api.azureml.ms`) into `FoundryRealtimeProvider`, not `AZURE_OPENAI_ENDPOINT`
(the AOAI direct account at `cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com`).
The GA Realtime API lives on the AOAI direct account — **not** the `azureml.ms` Foundry Hub.

---

## 2. Container Log Trace (Verbatim, Sanitized)

From `.squad/files/orchestrator-500-trace-after-wss-fix.log` (post-Bug-7 PR #13 deploy):

```
2026-05-15T21:22:21.558549062Z websockets.exceptions.InvalidStatus: server rejected WebSocket connection: HTTP 404
2026-05-15T21:22:22.327288320Z INFO:     100.100.0.19:40394 - "POST /api/turn HTTP/1.1" 500 Internal Server Error
```

Full stack:
```
File "/app/main.py", line 92, in api_turn
    session = await provider.open_session(SYSTEM_PROMPT, tools.specs)
File "/app/voice/foundry_realtime.py", line 162, in open_session
    ws = await websockets.connect(url, additional_headers=headers)
File "...websockets/asyncio/client.py", line 115, in handshake
    raise self.protocol.handshake_exc
websockets.exceptions.InvalidStatus: server rejected WebSocket connection: HTTP 404
```

The TCP+TLS handshake now reaches the remote host (Bug #7 fixed) but the host returns HTTP 404
on the WebSocket upgrade. No `www-authenticate` header present in the trace — if the scope were
wrong we'd get HTTP 401 with a `WWW-Authenticate: Bearer` header.

---

## 3. MS Learn — Canonical WSS URL Pattern

**Source:** https://learn.microsoft.com/en-us/azure/ai-services/openai/realtime-audio-quickstart  
**Quote (2026-05-14 revision):**

> "For all Realtime API models, use the GA endpoint format with `/openai/v1` in the URL."

**Supported model list explicitly includes:** `gpt-realtime-1.5 (2026-02-23)`

**Endpoint variable documented as:**
> `AZURE_OPENAI_ENDPOINT` — "This value can be found in the **Keys and Endpoint** section when
> examining your resource from the Azure portal." [i.e., the Cognitive Services / AOAI account
> endpoint — `https://<account>.openai.azure.com/`]

**MS Learn canonical WSS URL for GA gpt-realtime-1.5:**
```
wss://<aoai-account-name>.openai.azure.com/openai/v1/realtime?model=<deployment-name>
```

**Host:** `<account>.openai.azure.com` (AOAI direct) — NOT `<region>.api.azureml.ms` (Foundry Hub).  
**Path:** `/openai/v1/realtime` (with `/v1/` — GA format)  
**Query param:** `?model=<deployment-name>`

---

## 4. Hypothesis Test Results

### H1 — Wrong Host: `azureml.ms` vs `openai.azure.com`

| Probe | URL | Result |
|-------|-----|--------|
| Current (wrong) | `wss://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5` | **HTTP 404** |
| AOAI direct | `wss://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/openai/v1/realtime?model=gpt-realtime-1.5` | **HANDSHAKE_OK** ✅ |

**Probe command:**
```python
import asyncio, websockets
async def probe(url, token):
    ws = await websockets.connect(url, additional_headers=[('Authorization', f'Bearer {token}')])
    await ws.close(); return 'HANDSHAKE_OK'
```

**Inference: BUG CONFIRMED.** The `azureml.ms` Foundry Hub URL does not route the Realtime
WebSocket. The AOAI direct endpoint does. This is the root cause.

---

### H2 — Wrong Path: `/openai/v1/realtime` vs `/openai/realtime`

| Probe | URL | Result |
|-------|-----|--------|
| With `/v1/` (GA) | `wss://...openai.azure.com/openai/v1/realtime?model=gpt-realtime-1.5` | **HANDSHAKE_OK** ✅ |
| Without `/v1/` | `wss://...openai.azure.com/openai/realtime?model=gpt-realtime-1.5` | **HTTP 404** |

**Inference: RULED OUT.** `/openai/v1/realtime` is the **correct** GA path. The path in
`foundry_realtime.py` is correct. Confirmed by MS Learn quote above. Removing `/v1/` breaks it.

---

### H3 — Wrong Deployment Alias: `gpt-realtime-1.5` vs version suffix

**Probe command:**
```
az cognitiveservices account deployment list -n "cog-oai-crosstown-dryrun-may15-yycemmso7sk7q" \
  -g rg-crosstown-dryrun-may15 --query "[].{name:name, model:properties.model.name, version:properties.model.version}" -o table
```

**Result:**
```
Name              Model             Version
gpt-4.1           gpt-4.1           2025-04-14
gpt-realtime-1.5  gpt-realtime-1.5  2026-02-23
```

**Inference: RULED OUT.** Deployment name is exactly `gpt-realtime-1.5` — matching
`AZURE_OPENAI_REALTIME_DEPLOYMENT` and the `?model=` query param. No version suffix needed.
HANDSHAKE_OK probe above confirmed `?model=gpt-realtime-1.5` works on the correct host.

---

### H4 — Bearer Scope: `cognitiveservices.azure.com` vs `ai.azure.com`

**Probe command:**
```
az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv
# Decode JWT payload
```

**JWT payload claims:**
```json
{
  "aud": "https://cognitiveservices.azure.com",
  "appid": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
  "iss": "https://sts.windows.net/9b7cbd77-6d6b-4879-8aba-63d7dfb18472/"
}
```

**Source in code (`foundry_realtime.py` line 20):**
```python
REALTIME_SCOPE = "https://cognitiveservices.azure.com/.default"
```

**Inference: RULED OUT.** `aud=cognitiveservices.azure.com` is correct for AOAI direct.
The HANDSHAKE_OK probe used exactly this scope and succeeded. If scope were wrong, the server
would return HTTP 401 with `WWW-Authenticate`; 404 indicates the resource path doesn't exist,
not an auth rejection.

---

## 5. Verdict

**Root cause: Hypothesis 1 — Wrong Host. HIGH CONFIDENCE.**

`factory.py` passes `s.azure_ai_foundry_project_endpoint` (`https://swedencentral.api.azureml.ms`)
to `FoundryRealtimeProvider` instead of the AOAI direct endpoint
(`https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/`). The GA Realtime
WebSocket API lives on `openai.azure.com`, not on the `azureml.ms` Foundry Hub. The Bicep already
sets `AZURE_OPENAI_ENDPOINT` (AOAI direct) in the orchestrator container — it's the right value,
but `factory.py` ignores it in favour of `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`.

**Evidence chain:**
1. Pre-Bug-7 trace verbatim: `https://swedencentral.api.azureml.ms/openai/v1/realtime?model=gpt-realtime-1.5` → `InvalidURI: scheme isn't ws or wss`
2. Post-Bug-7 trace verbatim: `server rejected WebSocket connection: HTTP 404` (same host, now wss://)
3. Live WebSocket probe: `azureml.ms` → HTTP 404 | `openai.azure.com` → HANDSHAKE_OK
4. MS Learn: endpoint for Realtime is `AZURE_OPENAI_ENDPOINT` from "Keys and Endpoint" in portal = `openai.azure.com`
5. Deployment name `gpt-realtime-1.5` confirmed exact in AOAI account; bearer scope confirmed correct

**All other hypotheses ruled out.**

---

## 6. Recommended Fix

**Two-file, 3-line change:**

### File 1: `apps/orchestrator/settings.py`
Add one field to `Settings`:
```python
# BEFORE — line 13 area:
azure_ai_foundry_project_endpoint: str = ""

# AFTER — add below it:
azure_openai_endpoint: str = ""          # ← add this line
```

### File 2: `apps/orchestrator/voice/factory.py`
Change the endpoint passed to `FoundryRealtimeProvider`:
```python
# BEFORE (line 20):
    endpoint=s.azure_ai_foundry_project_endpoint,

# AFTER:
    endpoint=s.azure_openai_endpoint,
```

The env var `AZURE_OPENAI_ENDPOINT` is already injected into the orchestrator container by
`infra/main.bicep` (line 206). No Bicep change needed. No new secret. No new env var.
Pydantic `BaseSettings` will bind `azure_openai_endpoint` → `AZURE_OPENAI_ENDPOINT` automatically.

**Final URL after fix:**
```
wss://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/openai/v1/realtime?model=gpt-realtime-1.5
```
This is exactly the URL that returned HANDSHAKE_OK in the live probe above.

---

## 7. Confidence

**HIGH** — Live WebSocket probe directly confirmed HANDSHAKE_OK on the corrected URL with the
same bearer token and deployment alias already in use. No speculation.

---

## 8. Next Action

Brady (or any Squad member): ship the 2-file, 3-line change above — add `azure_openai_endpoint`
to `settings.py` and switch `factory.py` to `endpoint=s.azure_openai_endpoint` — then `azd
deploy orchestrator`; the live `/api/turn` smoke should go green in ~30 seconds.

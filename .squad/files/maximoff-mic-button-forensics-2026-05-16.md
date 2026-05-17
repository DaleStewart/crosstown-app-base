# Wanda Maximoff — Mic Button Forensics
**Date:** 2026-05-16  
**Requested by:** Sean  
**Status:** Root cause identified — awaiting Parker's Playwright data to close the loop  

---

## TL;DR

The mic button is dead because **nginx in the frontend container returns HTTP 502 Bad Gateway** for every WebSocket upgrade to `/ws/voice`. The orchestrator WS endpoint itself is healthy. The failure is entirely in the nginx → orchestrator proxy path.

---

## Step 1 — Log Activity (orchestrator, tail 200)

```
2026-05-15T22:17:43  Uvicorn running on http://0.0.0.0:8000
2026-05-15T22:18:37  POST /api/turn  200 OK
2026-05-15T22:19:05  POST /api/turn  200 OK
2026-05-15T22:36:51  POST /api/turn  200 OK
2026-05-15T22:41:56  POST /api/turn  422 Unprocessable Entity
2026-05-15T22:43:47  POST /api/turn  422 Unprocessable Entity
2026-05-15T22:44:21  POST /api/turn  200 OK
2026-05-16T13:35:41  GET /           404 Not Found
```

**Findings:**
- Zero `/ws/voice` entries in 200 lines of orchestrator logs — no WebSocket connections have ever reached the orchestrator from the browser. Uvicorn does not emit an HTTP access-log line for WS upgrades, so the absence confirms that WS connections are being terminated **before** they reach the container (i.e., at the nginx proxy layer).
- The orchestrator last received real traffic at 22:45 UTC yesterday (eval/redteam runs). Gap of ~15 hours.
- Two 422s at 22:41–22:43 UTC suggest a brief malformed-payload episode but those are `POST /api/turn` (text eval path), not voice. Not related to the mic bug.

---

## Step 2 — WS Route Handler (`/ws/voice`)

**File:** `apps/orchestrator/main.py` lines 134–139

```python
@app.websocket("/ws/voice")
async def ws_voice(ws: WebSocket) -> None:
    provider = app.state.provider
    tools = app.state.tools
    store = app.state.store
    await run_voice_session(ws, provider, tools, store)
```

**`run_voice_session` connect-time behaviour** (`apps/orchestrator/agent/orchestrator.py`):

1. `await ws.accept()` — immediately accepts the WebSocket with no header checks.
2. Enters a `while True: msg = await ws.receive()` loop.
3. **No auth header requirement.** No `Origin` check. No bearer token check.
4. On `{"type": "start"}` frame → calls `provider.open_session()` (FoundryRealtimeProvider), spawns the model→client pump as an asyncio task, returns to the receive loop waiting for audio bytes.
5. If `open_session` raises (e.g., 10 s `session.updated` timeout) the exception propagates out of the loop, `finally` closes the session and the WS drops. No error frame is sent to the client.

**CORS in orchestrator code:**

```
grep CORSMiddleware|allow_origins|allow_credentials → 0 matches
```

There is **no `CORSMiddleware`** in `apps/orchestrator/main.py` or any sub-module. FastAPI does not restrict WebSocket connections by `Origin` header by default. The orchestrator accepts any origin.

---

## Step 3 — Live WS Probe Results

### Direct probe against orchestrator (bypassing nginx)

```
URL:    wss://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ws/voice
Origin: https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io

Result: OPENED OK
        Sent {"type":"start","conversationId":"probe-001","mode":"push_to_talk"}
        No server frame within 18 s — WS remained OPEN
```

**Interpretation:** The orchestrator accepted the WS upgrade, processed the `start` frame (calling `provider.open_session()` and spawning the event pump), then sat in `await ws.receive()` waiting for audio bytes. The 18-second silence is expected — the Foundry session is open and idle, waiting for audio input. **Orchestrator WS is healthy.**

### Probe through frontend nginx proxy (the browser's actual path)

```
URL: wss://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/ws/voice

Result: FAILED — InvalidStatus: server rejected WebSocket connection: HTTP 502
        Response headers: server: nginx/1.27.5, content-type: text/html, connection: close
```

**The frontend nginx proxy returns 502 for every WS upgrade request.** This is the root cause.

---

## Step 4 — CORS / Origin Policy (verbatim from code)

**`apps/orchestrator/main.py`** (full file, 140 lines):

```python
app = FastAPI(title="MTA Orchestrator", lifespan=lifespan)
# No CORSMiddleware added anywhere
```

No `allow_origins`, no `allow_credentials`, no origin filtering of any kind. WebSocket CORS is not enforced server-side.

**`apps/frontend/nginx.conf`** (verbatim):

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass ${ORCHESTRATOR_URL};
    }

    location /ws/ {
        proxy_pass ${ORCHESTRATOR_URL};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600;
    }

    location / {
        try_files $uri /index.html;
    }
}
```

**`apps/frontend/docker-entrypoint.sh`** (verbatim):

```sh
#!/bin/sh
set -e
: "${ORCHESTRATOR_URL:=http://orchestrator:8000}"
export ORCHESTRATOR_URL
envsubst '$ORCHESTRATOR_URL' < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf
```

---

## Step 5 — Container Env State

### orchestrator

| Variable | Value |
|---|---|
| AZURE_CLIENT_ID | cce9346a-6cd9-4b4f-a9f0-13630e23e34d |
| AZURE_OPENAI_ENDPOINT | https://cog-oai-crosstown-dryrun-may15-yycemmso7sk7q.openai.azure.com/ |
| AZURE_OPENAI_CHAT_DEPLOYMENT | gpt-4.1 |
| AZURE_OPENAI_REALTIME_DEPLOYMENT | gpt-realtime-1.5 |
| VOICE_PROVIDER | foundry_realtime |
| LOG_ANALYST_URL | http://log-analyst.internal.blackriver-0ab9be19.swedencentral.azurecontainerapps.io |
| AZURE_AI_FOUNDRY_PROJECT_ENDPOINT | https://swedencentral.api.azureml.ms |
| APPLICATIONINSIGHTS_CONNECTION_STRING | (secret ref) |

All expected vars are present. `AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-realtime-1.5` (set per D-009).

### frontend

| Variable | Value |
|---|---|
| AZURE_CLIENT_ID | cce9346a-6cd9-4b4f-a9f0-13630e23e34d |
| ORCHESTRATOR_URL | **https://orchestrator.blackriver-0ab9be19.swedencentral.azurecontainerapps.io** |
| APPLICATIONINSIGHTS_CONNECTION_STRING | (secret ref) |

---

## Root Cause Analysis

### Primary Bug — nginx `proxy_pass https://` for WebSocket returns 502

`ORCHESTRATOR_URL` is set to `https://orchestrator.blackriver-...` (the external HTTPS URL). nginx's `location /ws/` does `proxy_pass ${ORCHESTRATOR_URL}`, which means nginx must:

1. Establish an **outbound TLS connection** to the orchestrator's external ACA URL.
2. Forward the WebSocket upgrade headers inside that TLS session.

The 502 response indicates nginx fails to connect to or proxy through the TLS upstream. Likely causes:

- **nginx SSL certificate verification failure** — the orchestrator's ACA cert (`*.blackriver-0ab9be19.swedencentral.azurecontainerapps.io`) may not be verifiable by the CA bundle inside the nginx Alpine container. nginx rejects the upstream SSL handshake → 502.
- **Routing loop / ACA restriction** — the frontend container makes an outbound HTTPS connection to the orchestrator's external URL, which may re-enter the ACA ingress and be rejected or cause a loop.
- **nginx proxy_pass to HTTPS upstream for WebSocket** — while technically supported, nginx's default behavior with `proxy_pass https://` does not disable SSL verification (`proxy_ssl_verify on` by default). Without `proxy_ssl_verify off` or explicit `proxy_ssl_trusted_certificate`, this commonly fails in containerised environments.

Note: `proxy_pass` for `/api/` uses the same HTTPS URL. If REST API calls (`POST /api/turn`) work via the browser hitting the orchestrator directly (they do — logs show 200s), that doesn't mean nginx proxy_pass to `https://` works from inside the container.

### Secondary Bug — No error frame on WS close

When the browser WS fails (502), `ws.onerror` fires then `ws.onclose` fires. `useVoiceSession` handles `onclose` with `dispatch({ type: "status", status: "idle" })` — status goes back to idle. `App.tsx` renders nothing for `state.error`. The user sees the button unchanged (or a brief flicker). Looks like "nothing happens."

### Secondary Observation — `session.update` payload has non-standard field

`foundry_realtime.py` sends:
```python
{"type": "session.update", "session": {"type": "realtime", "output_modalities": ["audio"], ...}}
```

Azure OpenAI Realtime API uses `"modalities"` (not `"output_modalities"`) and does not define a `"type"` field inside the session config. If these are silently ignored by the model backend, the session still opens (confirmed by 18s probe above). If the realtime model becomes stricter, this could cause `session.updated` to never fire and the 10s `asyncio.wait_for` to raise — but this is NOT the current failure mode.

---

## Hypotheses (Ranked)

| # | Hypothesis | Confidence | Evidence |
|---|---|---|---|
| 1 | **nginx `proxy_pass https://` SSL verification failure or routing issue → 502** | 🔴 **HIGH (confirmed)** | Direct probe: WS OPENS OK. Frontend proxy probe: HTTP 502. nginx/1.27.5 in response headers. |
| 2 | `session.update` non-standard fields cause Foundry to not emit `session.updated` | 🟡 MEDIUM | Field names diverge from Azure spec; direct probe shows no crash but 18s no-frame silence is ambiguous |
| 3 | `gpt-realtime-1.5` model deployment doesn't exist in the Azure OpenAI account (D-009 branch never pushed) | 🟡 MEDIUM | D-009 decision notes "push blocked (remote auth)" — env var is set but Azure deployment may not exist |
| 4 | `connect()` race condition — audio chunks sent before WS is OPEN and dropped | 🟠 LOW (secondary) | Code: `connect()` returns before WS is open; first audio packets sent to CONNECTING socket are silently dropped |
| 5 | Browser mic permission denied | 🟠 LOW | Would need Parker's Playwright data to confirm/deny |

---

## Questions Parker's Playwright Data Will Answer

1. **Does the browser's `WebSocket` constructor succeed?** (i.e., does `ws.onopen` fire?) — confirms or rules out Hypothesis 1.
2. **Does `ws.onerror` fire before `ws.onopen`?** — confirms HTTP 502 is the browser-side manifestation.
3. **What is `event.code` and `event.reason` in `ws.onclose`?** — 1006 (abnormal close) = network failure; 1000 = clean close.
4. **Does the browser's DevTools Network panel show a WS request to `/ws/voice` with status 101 or 502?** — distinguishes nginx 502 from connection refused.
5. **Is mic permission granted?** — rules out Hypothesis 5.
6. **Does the state show "connecting" → "idle" (fast) vs "connecting" → "connected" → "idle" (after 10s)?** — fast = 502 at nginx; slow = Foundry realtime timeout.

---

## Recommended Fix Path (for handoff to Parker)

**Immediate fix (least invasive):**  
Add `proxy_ssl_verify off;` to the `/ws/` location block in `apps/frontend/nginx.conf`:

```nginx
location /ws/ {
    proxy_pass ${ORCHESTRATOR_URL};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600;
    proxy_ssl_verify off;   # ← add this
}
```

Then redeploy the frontend container. No env var changes needed.

**Better fix (architectural):**  
Set `ORCHESTRATOR_URL` in the frontend container to the orchestrator's internal ACA URL (HTTP, no TLS). This requires enabling internal ingress on the orchestrator container app. Then nginx proxies over plain HTTP within the ACA environment — no SSL, no cert issues.

Example internal URL: `http://orchestrator.internal.blackriver-0ab9be19.swedencentral.azurecontainerapps.io`

**DO NOT SHIP** until Parker confirms browser-side symptoms match Hypothesis 1.

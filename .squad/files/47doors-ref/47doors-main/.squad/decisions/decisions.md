# Decisions Log

**Last Updated:** 2026-04-09T03:30Z

## Active Decisions

### WebSocket Bridge for ACS→Azure OpenAI Audio Relay — 2026-04-09

**Author:** Tank  
**Status:** Implemented & Deployed  
**Commit:** b2d7abc

Phone calls to +19132171946 connected (call answered) but produced dead air — no audio in either direction. ACS media streaming was configured to connect directly to Azure OpenAI Realtime API's WebSocket, but ACS had no managed identity to authenticate with and Azure OpenAI only accepted Entra ID auth. Additionally, CloudEvents callback parsing rejected all events, hiding `MediaStreamingFailed` diagnostics.

**Decision:** Route ACS media streaming through a backend WebSocket bridge (`/ws/acs-media`) instead of connecting ACS directly to Azure OpenAI. The backend authenticates to Azure OpenAI using its existing managed identity.

```
PSTN → ACS → WS [backend /ws/acs-media] → WS [Azure OpenAI Realtime API]
```

**Files Changed:** `backend/app/api/media_ws.py` (new, 296 lines), `backend/app/services/azure/phone.py` (transport_url), `backend/app/api/phone.py` (CloudEvents parsing), `backend/app/main.py` (route registration)

**Impact:** Audio now flows bidirectionally on answered PSTN calls. All 447 tests pass. No infra changes required.

---

### Fix ACS CallbackUri for Container Apps — 2026-04-09

**Author:** Tank  
**Status:** Implemented & deployed  
**Commit:** 365271d

Inbound phone calls failed with "CallbackUri invalid" (400) because Container Apps TLS termination caused `request.base_url` to resolve to `http://` (internal address). ACS requires HTTPS public URLs.

**Decision:** Reconstruct callback URL from `X-Forwarded-Proto` + `Host` request headers (set by Container Apps ingress), with `PHONE_CALLBACK_BASE_URL` config setting as explicit override.

**Files Changed:** `backend/app/api/phone.py`, `backend/app/services/azure/phone.py`, container env

**Impact:** Phone calls now answer correctly. Future services needing public callbacks should follow the same pattern.

---

### Playwright Eval Suite — Deployment Quality Gate — 2026-04-09

**Author:** Mouse  
**Status:** Implemented  
**Files Created:** `frontend/tests/e2e/eval.spec.ts`

Made `playwright.config.ts` environment-portable: `BASE_URL` env var overrides `baseURL`, `webServer` block skipped when targeting live deployment.

**Decision:** Created 24-test eval suite covering homepage, backend health, chat, KB quality, sessions, error handling, voice UI, performance. KB quality assertions are hard failures (demo quality gate, not smoke test). Health endpoint threshold set to 10s (Azure Container Apps cold-start).

**Key Findings:** 2 KB quality failures are real demo risks:
1. Registration queries trigger clarification loop instead of answering
2. Financial aid queries misroute to IT Support instead of Financial Aid

**Impact:** Eval can be run against any environment. Existing tests need refactor to use `BACKEND_URL` env var. WCAG violations in accessibility tests are real and need fixing.

---

### Dedicated Nginx Location Block for SSE Streaming — 2026-04-09

**Author:** Tank  
**Status:** Implemented & Deployed  
**Commits:** db2d48c, dd66ad6  

Live transcript page (`/live`) connected successfully but displayed no transcript text. SSE events from `/api/phone/transcripts/stream` were silently buffered by nginx because the single `/api/` location block was configured with WebSocket semantics (`Connection "upgrade"`, no `proxy_buffering off`).

**Decision:** Added dedicated `location /api/transcripts/stream` block in `frontend/nginx.conf` with SSE-specific proxy settings:
- `proxy_buffering off` + `proxy_cache off` — disables nginx response buffering
- `proxy_set_header Connection ""` — uses HTTP keep-alive instead of WebSocket upgrade
- `proxy_read_timeout 86400` — allows long-lived SSE connections (24h)

The existing `/api/` block remains unchanged for regular REST calls and WebSocket (`/api/realtime/ws/`).

**Rationale:** SSE and WebSocket have fundamentally different proxy requirements:
- WebSocket: needs `Connection "upgrade"` + `Upgrade` header
- SSE: needs `Connection ""` (keep-alive) + `proxy_buffering off`

Nginx longest-prefix matching ensures `/api/transcripts/stream` matches before falling through to general `/api/` block.

**Files Changed:** `frontend/nginx.conf` — added SSE location block before existing `/api/` block

**Impact:** Live transcript viewer now functional. Change is additive. Existing `/api/` block untouched, so WebSocket and REST traffic unaffected. If additional SSE endpoints added, they should nest under `/api/transcripts/` (already covered by prefix match) or get own location block.

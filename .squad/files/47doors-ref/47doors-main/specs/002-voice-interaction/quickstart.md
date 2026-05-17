# 🚀 Voice Feature — Developer Quickstart

> **Feature branch**: `002-voice-interaction` | **Spec**: [spec.md](./spec.md) | **API contract**: [contracts/voice-api.yaml](./contracts/voice-api.yaml)

The voice feature adds a real-time spoken conversation channel to the 47 Doors Support Agent using the Azure OpenAI GPT-4o Realtime API over WebRTC (browser) or direct WebSocket (phone bridge via Azure Communication Services). Audio travels **directly** from the browser to Azure — nothing audio-related passes through the backend. The backend only relays tool call results via a lightweight WebSocket connection. For phone calls to +1 (913) 217-1946, audio flows through an ACS media streaming bridge at `backend/app/api/media_ws.py`.

---

## 1. Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| Browser | Chrome 90+, Firefox 85+, Edge 90+, or Safari 15+ (WebRTC required) |
| Azure OpenAI | Only needed for live mode — see [Mock Mode](#2-mock-mode-no-azure-required) |

For **live mode** you additionally need an Azure OpenAI resource with a `gpt-4o-realtime-preview` deployment. Supported regions: `eastus2`, `swedencentral`, `westus3`.

---

## 2. Mock Mode (No Azure Required)

Mock mode is the **default**. It simulates the Realtime API using the existing text pipeline and returns canned/text-synthesised responses. No microphone permission is required.

```bash
# ── Terminal 1: Backend ──────────────────────────────────────────────────────
cd backend
cp .env.example .env      # MOCK_MODE=true is already set in .env.example
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# ── Terminal 2: Frontend ─────────────────────────────────────────────────────
cd frontend
npm install
npm run dev               # Vite proxy forwards /api → http://127.0.0.1:8000
```

Open `http://localhost:5173` — the 🎤 microphone button appears in the chat input area.

> **What mock mode does**
> - Calls `GET /api/realtime/health` on load → `{ "realtime_available": true, "mock_mode": true }`
> - `POST /api/realtime/session` returns a synthetic token (never leaves the backend)
> - Tool calls route through the real 3-agent pipeline; responses are delivered as text
> - The mic button shows all visual states (listening → processing → responding) with simulated timing
> - Great for UI work, demos, and running CI without Azure credentials

---

## 3. Live Mode (Azure Required)

### 3.1 Environment Variables

Add these to `backend/.env` (do **not** commit secrets):

```dotenv
# Switch to live mode
MOCK_MODE=false

# Azure OpenAI — existing deployment (used by text chat)
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Realtime API — gpt-4o-realtime-preview deployment
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
```

> ⚠️ **Managed Identity (Azure Container Apps)**: When deployed to Azure Container Apps via `azd up`, the backend uses `ManagedIdentityCredential` — no API key is needed. The Container App's system-assigned managed identity must have the `Cognitive Services OpenAI User` role on the Azure OpenAI resource. API key auth is disabled by Azure subscription policy (`disableLocalAuth: true`).
>
> **Local development**: For local development, set `AZURE_OPENAI_API_KEY` in `.env` if your Azure OpenAI resource allows API key auth. The current `AzureRealtimeService` uses `ManagedIdentityCredential` which only works in Azure Container Apps — for local dev, use mock mode (`MOCK_MODE=true`).
>
> **Docker**: Ensure `backend/.dockerignore` excludes `.env` to prevent secrets from being baked into container images.

### 3.2 Required Azure Deployment

The Realtime API requires a separate model deployment. Supported regions:

| Region | Status |
|---|---|
| `eastus2` | GA |
| `swedencentral` | GA |
| `westus3` | GA |

Provision via Bicep (see `infra/`) or the Azure Portal → Azure OpenAI → Model deployments → Add → `gpt-4o-realtime-preview`.

### 3.3 Start

```bash
# Backend (same as mock mode)
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (same as mock mode)
cd frontend && npm run dev
```

The microphone button is now backed by the real Realtime API. A WebRTC peer connection is established between the browser and Azure OpenAI directly.

---

## 4. Codespaces Notes

Vite proxies `/api` to the backend automatically — **do not set `VITE_API_BASE_URL` to a localhost URL** inside Codespaces (leave it as empty string or unset).

```dotenv
# frontend/.env.local inside Codespaces — leave this blank
VITE_API_BASE_URL=
```

| Port | Service | Forward? |
|---|---|---|
| `5173` | Vite dev server (frontend) | ✅ Yes |
| `8000` | uvicorn (backend) | ✅ Yes |

WebRTC works in Codespaces — the browser handles the peer connection to Azure OpenAI directly. The backend WebSocket (`/api/realtime/ws`) flows through the Vite proxy, which supports WebSocket upgrades.

---

## 5. Key Files

### Backend

| File | Purpose |
|---|---|
| `backend/app/api/realtime.py` | `POST /realtime/session`, `GET /realtime/ws`, `GET /realtime/health` |
| `backend/app/services/interfaces.py` | `RealtimeServiceInterface` — implemented by both mock and Azure services |
| `backend/app/services/mock/realtime.py` | Mock realtime service (simulates tool calls) |
| `backend/app/services/azure/realtime.py` | Azure OpenAI Realtime API integration |
| `backend/app/models/voice.py` | `VoiceMessage`, `RealtimeSessionResponse`, `ToolDefinition` |
| `backend/app/core/config.py` | Voice config fields (`voice_enabled`, `realtime_deployment`, etc.) |

### Frontend

| File | Purpose |
|---|---|
| `frontend/src/hooks/useVoice.ts` | WebRTC state machine + WS relay hook |
| `frontend/src/components/VoiceMicButton.tsx` | Mic toggle with 6 visual states |
| `frontend/src/components/VoiceTranscript.tsx` | Real-time transcript bubbles in chat thread |
| `frontend/src/components/VoiceStatusIndicator.tsx` | Connection status banner |
| `frontend/src/types/voice.ts` | `VoiceState`, `VoiceMessage`, `RealtimeSessionResponse` types |
| `frontend/src/containers/ChatContainer.tsx` | Modified to integrate voice components |

### Config & Infra

| File | Purpose |
|---|---|
| `backend/.env.example` | Environment variable template |
| `infra/` | Bicep templates — includes `gpt-4o-realtime-preview` deployment |
| `specs/002-voice-interaction/contracts/voice-api.yaml` | OpenAPI 3.1 contract for all voice endpoints |

---

## 6. API Quick Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/realtime/health` | GET | Is voice available? Check before showing the mic button |
| `/api/realtime/session` | POST | Get an ephemeral token (TTL ≤ 60 s) for WebRTC auth |
| `/api/realtime/ws` | WS | Tool call relay (connect with `?session_id=…&token=…`) |

Full schema: [`contracts/voice-api.yaml`](./contracts/voice-api.yaml)

---

## 7. Running Tests

```bash
# ── Backend voice tests ───────────────────────────────────────────────────────
cd backend
python -m pytest tests/test_voice/ -v

# Run all backend tests (voice + existing, excluding GPT-4o evals)
python -m pytest -x --ignore=tests/test_gpt4o_evals.py

# ── GPT-4o model evals (requires az login) ────────────────────────────────────
az login                              # authenticate with DefaultAzureCredential
python -m pytest tests/test_gpt4o_evals.py -v   # 97 tests: intent, PII, sentiment, entities, urgency, e2e

# Run ALL backend tests (338 unit/mock + 97 GPT-4o evals)
python -m pytest -x

# ── Frontend voice tests ──────────────────────────────────────────────────────
cd frontend
npm test -- --filter voice          # Vitest unit tests

# E2E (requires both backend and frontend running)
npx playwright test tests/voice/
```

Backend test coverage areas:

| Test file | What it covers |
|---|---|
| `test_config.py` | Voice config fields, `voice_enabled` flag, mock-mode defaults |
| `test_models.py` | `VoiceMessage`, `RealtimeSessionResponse` Pydantic validation |
| `test_mock_service.py` | Mock Realtime service tool call simulation |
| `test_endpoints.py` | `POST /realtime/session`, WS handshake, `GET /realtime/health` |
| `test_pii_filter.py` | PII scrubbing of transcripts before persistence |
| `test_evals.py` | 74 mock-based eval tests (intent routing, PII, sentiment, entities, urgency) |
| `test_gpt4o_evals.py` | 97 GPT-4o model eval tests via `DefaultAzureCredential` (requires `az login`) |

Frontend test coverage areas:

| Test file | What it covers |
|---|---|
| `VoiceMicButton.test.tsx` | All 6 visual states, keyboard activation (Enter/Escape) |
| `useVoice.test.ts` | WebRTC state machine, WS message handling, degradation fallback |
| `voice-e2e.spec.ts` | Full mock-mode voice session end-to-end flow |

---

## 8. Architecture: How a Voice Request Works

```
1. User clicks 🎤
2. Frontend calls GET /api/realtime/health → confirms voice available
3. Frontend calls POST /api/realtime/session → receives { token, endpoint, deployment }
4. Frontend opens RTCPeerConnection to Azure OpenAI (WebRTC, using ephemeral token)
5. Frontend connects WebSocket to /api/realtime/ws?session_id=…&token=…
6. User speaks → Azure OpenAI streams audio, detects intent, invokes a tool
7. Azure sends tool_call_request to backend relay → backend executes 3-agent pipeline
8. Backend returns tool result → Azure OpenAI speaks response to student
9. Transcript appended to chat thread with 🔊 icon (input_modality="voice")
10. User clicks 🎤 again or presses Escape → WebRTC + WS connections closed
```

---

## 9. Troubleshooting

| Symptom | Fix |
|---|---|
| Mic button not shown | Check `GET /api/realtime/health` → `realtime_available` should be `true`. In mock mode this is always true. Check backend is running on port 8000. |
| Mic permission dialog never appears | Expected in mock mode (no mic needed). In live mode, confirm the page is served over HTTPS or `localhost`. |
| WebRTC connection fails | Check browser console for ICE errors. In live mode verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_REALTIME_DEPLOYMENT` are set. Ensure frontend uses `{endpoint}/openai/v1/realtime/calls` for WebRTC SDP exchange. |
| Auth fails with `disableLocalAuth` | Your Azure subscription enforces managed identity. Remove `AZURE_OPENAI_API_KEY` from `.env`. Deploy to Azure Container Apps and ensure the MI has `Cognitive Services OpenAI User` role. |
| `.env` overrides managed identity | Ensure `backend/.dockerignore` excludes `.env`. Rebuild: `azd deploy`. |
| Tools not executing | Check uvicorn logs for WebSocket messages. Verify the 3-agent pipeline is healthy (`GET /api/health`). |
| Mock mode not responding | Confirm `MOCK_MODE=true` in `backend/.env`. Restart uvicorn after `.env` changes. |
| WS closes with code 4001 | Ephemeral token expired (TTL ≤ 60 s). Request a new token via `POST /api/realtime/session` before connecting. |
| WS closes with code 4002 | `session_id` not found. Confirm the UUID in query params matches a live session. |
| Text chat broken after voice | Should never happen — voice uses separate connections. File a bug and check `ChatContainer.tsx` state isolation. |

---

## 10. Constitution Compliance Reminders

> These are non-negotiable per [constitution.md](../../.specify/memory/constitution.md).

- 🔒 **No raw audio stored** — only PII-filtered transcripts (Principle III)
- 🔒 **Ephemeral tokens ≤ 60 s TTL, single-use** (Voice Channel Security)
- 🔒 **No API key exposure** — token is the only credential the frontend ever sees
- ♿ **Keyboard accessible mic button** — Space/Enter to activate, Escape to stop (Principle VI)
- ♿ **ARIA live regions** for all voice state changes (Principle VI)
- 📉 **Graceful degradation** — if voice fails, text chat continues unaffected (Principle VII)
- 🧪 **Tests first** — write failing tests before implementing each phase (Principle V)

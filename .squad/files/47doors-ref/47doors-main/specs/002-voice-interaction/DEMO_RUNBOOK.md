```
╔══════════════════════════════════════════════════════════════════════════════╗
║   🎤  4 7   D O O R S   —   V O I C E   F E A T U R E   R U N B O O K  🎤  ║
║              speak naturally · be heard · get answers                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> 👥 **Audience**: EDU customers, stakeholders, internal demos
> 📅 **Last updated**: 2026-04-21 &nbsp;|&nbsp; ⏱️ **Estimated demo time**: 12–15 minutes &nbsp;|&nbsp; 🟢 **Status**: Production (revision `azd-1776792457`)

```
Demo Readiness  [████████████████████] 100%  ✅ All systems go
Azure Live      [████████████████████] 100%  ✅ Connected to Azure OpenAI (MOCK_MODE=false)
Test Coverage   [████████████████████] 100%  ✅ 435 backend tests passing
```

---

## 🎯 Demo Overview

The **47 Doors Universal Front Door Support Agent** now speaks. Students can click a single microphone button and have a natural spoken conversation with the same AI pipeline that powers text chat — or call +1 (913) 217-1946 for phone-based voice support via Azure Communication Services — getting ticket confirmations, knowledge article summaries, and escalation notices, all by voice. This demo shows how a university can replace dozens of disconnected support portals with **one trusted digital colleague** that works whether you type, talk, or call.

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 Student speaks  →  🧠 3-Agent Pipeline  →  🔊 AI replies │
│                                                             │
│  QueryAgent ──► RouterAgent ──► ActionAgent                 │
│      │               │               │                      │
│   🔍 Intent       🗺️ Route        🎫 Ticket                 │
│   Detection      Selection        Creation                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧰 Version Matrix & Compatibility

```
┌─────────────────────────────────────────────────────────────────────┐
│  ⚙️  SYSTEM REQUIREMENTS & COMPATIBILITY MATRIX                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 🐍 Runtime & Framework Versions

| 🔧 Component | 📌 Required | 🏷️ Recommended | 🟢 Status |
|---|---|---|---|
| 🐍 Python | `3.11+` | `3.12` | ✅ Supported |
| 🟩 Node.js | `18+` | `20 LTS` | ✅ Supported |
| ⚡ FastAPI | `0.109+` | `0.115+` | ✅ Supported |
| ⚛️ React | `18.x` | `18.3+` | ✅ Supported |
| ⚡ Vite | `5.x` | `5.2+` | ✅ Supported |

### ☁️ Azure OpenAI Model Versions

| 🤖 Model | 🏷️ Version | 🎯 Use Case | 🟢 Status |
|---|---|---|---|
| 🧠 GPT-4o | `2024-05-13` | Text chat pipeline | ✅ Active |
| 🎤 GPT-4o Realtime Preview | `2024-10-01` | Voice / WebRTC | ✅ Active |
| 🔊 GPT-4o Audio Preview | `2024-10-01` | Audio fallback | 🟡 Optional |

### 🌐 Browser Compatibility

| 🌐 Browser | 📌 Min Version | 🎤 WebRTC | 🔊 Audio API | 🟢 Recommended |
|---|---|---|---|---|
| 🟡 Chrome | `90+` | ✅ Full | ✅ Full | ⭐ Best |
| 🔵 Edge | `90+` | ✅ Full | ✅ Full | ⭐ Best |
| 🟠 Firefox | `85+` | ✅ Full | ✅ Full | ✅ Good |
| 🔘 Safari | `15+` | ⚠️ Partial | ⚠️ Partial | 🟡 Caution |
| 🔴 IE / Legacy | Any | ❌ None | ❌ None | ❌ Unsupported |

> ⚠️ **Safari note**: WebRTC and Web Audio API support varies. Test before customer demos on macOS/iOS.

### 💻 Operating System Support

| 💻 Platform | 🟢 Support Level | 📝 Notes |
|---|---|---|
| 🪟 Windows 10/11 | ✅ Full | Recommended for demos |
| 🍎 macOS 12+ | ✅ Full | Check Safari mic permissions |
| 🐧 Linux (Ubuntu 22+) | ✅ Full | Chrome/Firefox only |
| ☁️ GitHub Codespaces | ✅ Full | Leave `VITE_API_BASE_URL` empty |
| 🐳 Docker Desktop | ✅ Full | `docker-compose up` — one command |

---

## ✅ Pre-Demo Checklist

> ⏰ Run through this list **5 minutes before** you start the demo.

```
Overall Readiness  [░░░░░░░░░░░░░░░░░░░░]   0%  ← fill as you check each item
```

| # | 🔍 Check | 💡 Detail | 🟢 Status |
|---|---|---|---|
| 1️⃣ | 🌐 **Browser open** | Chrome 90+, Firefox 85+, or Edge 90+ | ☐ |
| 2️⃣ | 🎙️ **Microphone tested** | Settings → Privacy → Microphone → Allow | ☐ |
| 3️⃣ | ☁️ **Azure Container App deployed** | `azd up` completed · `https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/health` returns `healthy` | ☐ |
| 4️⃣ | 🖼️ **Frontend reachable** | [Container App URL](https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io) loads the UI (or Vite dev if running locally) | ☐ |
| 5️⃣ | 🔑 **Azure subscription active** | `az account show` confirms sub `ME-MngEnvMCAP262307-segayle-1` · `azd auth login` completed | ☐ |
| 6️⃣ | 🤖 **Azure OpenAI connected** | `MOCK_MODE=false` · live `gpt-4o` + `gpt-4o-realtime-preview` deployments on `frontdoor-6wfum6gndxawy-openai` | ☐ |
| 7️⃣ | 🔊 **Audio output working** | System volume up · headset or speakers confirmed | ☐ |
| 8️⃣ | 🛡️ **Fallback ready** | If voice fails → text chat **always** works · stay calm | ☐ |

```
✅ All 8 checked?  [████████████████████] 100%  🟢 Ready to demo!
⚠️  6-7 checked?  [████████████████░░░░]  80%  🟡 Proceed with caution
❌  <6 checked?   [████████░░░░░░░░░░░░]  40%  🔴 Stop — fix issues first
```

> 💡 **Codespaces?** Leave `VITE_API_BASE_URL` blank — Vite proxies `/api` to `127.0.0.1:8000` automatically. Both port **5173** and port **8000** must be forwarded.

---

## 🚀 Start Commands

```
┌──────────────────────────────────────────────────────┐
│  🚀  LAUNCH SEQUENCE — CHOOSE YOUR PATH              │
├──────────────────────────────────────────────────────┤
│  Option A  ── ☁️  Azure Container Apps (Recommended) │
│  Option B  ── 🐳 Docker (local alternative)          │
│  Option C  ── 💻 Local Dev (debugging fallback)      │
│  Option D  ── ☁️  GitHub Codespaces (cloud dev)       │
└──────────────────────────────────────────────────────┘
```

### ☁️ Option A — Azure Container Apps *(Recommended)*

This is the **primary demo path**. Azure resources are live and verified.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  ☁️  LIVE AZURE INFRASTRUCTURE                                                │
├───────────────────────────────────────────────────────────────────────────────┤
│  🌐 Container App   https://frontdoor-6wfum6gndxawy-backend                  │
│                     .blackflower-446b9850.eastus2.azurecontainerapps.io       │
│  📦 Resource Group   rg-vvoice                                                │
│  🧠 OpenAI Endpoint  frontdoor-6wfum6gndxawy-openai.openai.azure.com         │
│  🤖 GPT-4o Deploy    gpt-4o                                                  │
│  🎤 Realtime Deploy  gpt-4o-realtime-preview                                 │
│  🗄️ Cosmos DB        frontdoor-zfyhb6f72odyg-cosmos.documents.azure.com      │
│  🔍 AI Search        frontdoor-6wfum6gndxawy-search.search.windows.net       │
│  🐳 Container Reg    frontdoor6wfum6gndxawyacr.azurecr.io                    │
│  📍 Region           eastus2                                                  │
│  💳 Subscription     ME-MngEnvMCAP262307-segayle-1                            │
│  🔧 Mock Mode        false                                                    │
└───────────────────────────────────────────────────────────────────────────────┘
```

```bash
# 1️⃣  Authenticate (once per machine)
azd auth login

# 2️⃣  Provision + deploy everything (first time, ~5 min)
azd up

# 2b️⃣  Subsequent deploys (code changes only)
azd deploy

# 3️⃣  Get the live URL
azd env get-values | grep AZURE_CONTAINERAPP_URL
```

```bash
# The frontend SPA is served from the same Container App host.
# Live URL:
# https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io
```

> 💡 **Subscription**: `ME-MngEnvMCAP262307-segayle-1` · **Region**: `eastus2`

### 🐳 Option B — Docker *(Local Alternative)*

```bash
docker-compose up
# 🖼️ Frontend: http://localhost:5173
# 🖥️ Backend:  http://localhost:8000
```

### 💻 Option C — Local Dev *(Debugging Fallback)*

```bash
# 🖥️ Terminal 1 — Backend
cd backend
cp .env.example .env          # Set MOCK_MODE=false + Azure creds for live mode
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# 🖼️ Terminal 2 — Frontend
cd frontend
npm install
npm run dev                   # Opens http://localhost:5173
```

### ☁️ Option D — GitHub Codespaces

```bash
# Same as Option C — Vite proxy handles /api routing
# ⚠️  DO NOT set VITE_API_BASE_URL to a localhost URL inside Codespaces
# Leave it as empty string in frontend/.env.local:
echo "VITE_API_BASE_URL=" > frontend/.env.local
```

### 🩺 Health Check *(Verify before demoing)*

> 💡 The live Container App URL is hardcoded below. Both endpoints have been verified ✅.

```bash
# ☁️ Azure (primary — LIVE)
curl https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/health
# ✅ Verified: LLM connecting, services up: ticketing, knowledge_base, session_store

curl https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/realtime/health
# ✅ Verified: { "realtime_available": true, "mock_mode": false, "voice_enabled": true }

# 💻 Local fallback
# curl http://localhost:8000/api/health
# curl http://localhost:8000/api/realtime/health
```

```
Backend  Health  [████████████████████] ✅  healthy (ticketing ✅ · knowledge_base ✅ · session_store ✅)
Realtime Health  [████████████████████] ✅  available  (mock_mode: false · voice_enabled: true — Azure Live)
Frontend Load    [████████████████████] ✅  frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io
```

---

## 🎯 Demo Prompts Quick Reference

> **Cheat sheet** — copy-paste or say these during the demo. Each is proven to hit a specific intent and department.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  🧠  INTENT CLASSIFIER — WHAT TO TYPE OR SAY                                     │
├──────────────────────┬───────────────┬───────────────────────────────────────────┤
│  🎯 Intent           │  🏢 Department │  💬 Demo Prompt                            │
├──────────────────────┼───────────────┼───────────────────────────────────────────┤
│  TECHNICAL_SUPPORT   │  IT           │  "I forgot my password and can't log      │
│                      │               │   into Canvas"                            │
├──────────────────────┼───────────────┼───────────────────────────────────────────┤
│  BILLING             │  FINANCIAL_AID│  "My financial aid was supposed to be     │
│                      │               │   disbursed last week but my account      │
│                      │               │   still shows a balance"                  │
├──────────────────────┼───────────────┼───────────────────────────────────────────┤
│  ACADEMIC_RECORDS    │  REGISTRAR    │  "How do I request an official transcript │
│                      │               │   for my grad school application?"        │
├──────────────────────┼───────────────┼───────────────────────────────────────────┤
│  ACCOUNT_MANAGEMENT  │  IT           │  "I need to update my mailing address     │
│                      │               │   before graduation"                      │
├──────────────────────┼───────────────┼───────────────────────────────────────────┤
│  GENERAL             │  IT           │  "Hi there!"                              │
└──────────────────────┴───────────────┴───────────────────────────────────────────┘
```

### 🔥 High-Impact Demo Scenarios

| # | Scenario | What to Say/Type | What Happens |
|---|----------|-----------------|--------------|
| 1 | 🎫 **Ticket creation** | "I forgot my password and can't log into Canvas" | Intent: TECHNICAL_SUPPORT → IT dept → ticket created + KB articles + SLA |
| 2 | 💰 **Financial query** | "My financial aid was supposed to be disbursed last week but my account still shows a balance" | Intent: BILLING → FINANCIAL_AID dept → ticket + aid disbursement KB |
| 3 | 📜 **Records request** | "How do I request an official transcript for my grad school application?" | Intent: ACADEMIC_RECORDS → REGISTRAR dept → transcript process KB |
| 4 | 👤 **Profile update** | "I need to update my mailing address before graduation" | Intent: ACCOUNT_MANAGEMENT → IT dept → account update instructions |
| 5 | ⚠️ **Escalation** | "I want to appeal my grade" | Intent: POLICY_EXCEPTION → ESCALATE_TO_HUMAN → human handoff demo |
| 6 | 🗣️ **Human request** | "Can I speak to a real person?" | Intent: HUMAN_REQUEST → ESCALATE_TO_HUMAN → escalation flow |
| 7 | 😤 **Frustrated student** | "This is urgent — I can't submit my assignment tonight and Canvas keeps crashing!" | Sentiment: FRUSTRATED/URGENT → priority bumped to HIGH |
| 8 | 🔄 **Follow-up** | "Can you check the status of that ticket?" | Shows session continuity (voice or text) |
| 9 | 👋 **Greeting** | "Hi there!" | Intent: GENERAL → friendly response, awaits real question |

### 🚨 Escalation Triggers (Keywords That Force Human Handoff)

These intents in the `RouterAgent` always escalate to a human:

```
grade_appeal · withdrawal_request · waiver_request · refund_request · request_human · speak_to_person
```

> 💡 **Pro tip**: For voice demos, use prompts #1 and #2 — they produce the most complete responses (ticket + KB + SLA). Follow with #8 to show session continuity.

---

## 🎬 Demo Sequence (12–15 Minutes)

```
┌────────────────────────────────────────────────────────────────────┐
│  🎬  DEMO TIMELINE                                                 │
├──────┬──────────────────────────────────────────────┬─────────────┤
│  ⏱️  │  🎭 Scene                                     │  📊 Progress │
├──────┼──────────────────────────────────────────────┼─────────────┤
│ 0–3m │  🎭 Scene 1 — The 47 Doors Problem           │ [████░░░░░░] │
│ 3–7m │  🎤 Scene 2 — Voice Interaction              │ [████████░░] │
│ 7–10m│  🔍 Scene 3 — Observability & Trust          │ [████████░░] │
│10–12m│  🛡️  Scene 4 — Graceful Degradation           │ [████████░░] │
│12–14m│  🔭 Scene 5 — What's Next                    │ [████████░░] │
└──────┴──────────────────────────────────────────────┴─────────────┘
```

---

### 🎭 Scene 1 — The 47 Doors Problem *(~3 min)*

> 🟢 **Status**: Opening act — set the context

**📺 What to show:** The chat UI with text conversation working normally.

**🎙️ Talk track:**

> *"Imagine being a first-year student at a large university. You have a password problem — but is that IT? Or is it your course portal? Maybe it's your library login? At most universities, there are literally **47 different front doors** for support. Students don't know which door to knock on, so they knock on all of them and wait."*

> *"47 Doors is the answer to that. One trusted digital colleague that knows every department, every process, and every knowledge article — and routes your request to exactly the right team."*

1. ⌨️ **Type** in the chat: `"I forgot my password and can't log into Canvas"`
2. 👀 **Show** the ticket ID returned, the KB articles, and the SLA estimate
3. 📍 **Point out**: One input → intent detected → ticket created → KB surfaced → SLA communicated

```
Student types  ──►  🧠 Intent Detection  ──►  🗺️ Router  ──►  🎫 Ticket + 📚 KB + ⏱️ SLA
                         [████████████]           [████]         [████████████████]
```

> *"This is what we built for text. Today, I'm going to show you the same experience — but spoken out loud."*

---

### 🎤 Scene 2 — Voice Interaction *(~4 min)*

> 🟢 **Status**: The money shot — this is what they came to see

**📺 What to show:** The full voice round-trip — click mic, speak, hear a response, see the transcript.

**🎙️ Talk track:**

> *"Let me show you what it looks like when a student just wants to talk."*

1. 👆 **Point to** the 🎤 microphone button in the chat input area
   > *"One button. That's the entire voice interface."*

2. 🖱️ **Click the mic button** — the button pulses 🟢 green
   > *"The browser asks for mic permission — we request it, the student grants it, and we're live. Notice the status banner at the top: it says 'Listening...'"*

3. 🗣️ **Speak clearly**: *"I forgot my password and can't log into Canvas"*
   > *"Speak naturally. No commands, no keywords — just say what you need."*

   ```
   🎙️ Listening...    [████████░░░░░░░░░░░░]  VAD active · detecting speech
   ```

4. ⏳ **While processing** — point to the spinner state
   > *"The agent heard me finish speaking. Now it's running the same 3-agent pipeline we just saw in text — intent detection, routing, action. That's the WebSocket tool relay working in the background."*

   ```
   🧠 Processing...   [████████████████░░░░]  3-agent pipeline running
   ```

5. 🔊 **When the agent responds** — point to the transcript bubble with 🔊 icon
   > *"The agent speaks the answer back AND adds it to the chat thread with a speaker icon so there's always a written record. Notice transcripts appear inline in the chat thread — user speech with a 🎤 microphone icon and assistant responses with a 🔊 speaker icon. No audio is stored — only this PII-filtered transcript."*

   ```
   ✅ Response ready  [████████████████████]  🔊 Audio + 📝 Transcript delivered
   ```

6. 🗣️ **Ask a follow-up question verbally**: *"Can you check the status of that ticket?"*
   > *"Now I'm asking a follow-up without re-explaining anything. The session context is shared — voice and text are the same session."*

7. 🖱️ **Click mic button again** to stop — status returns to 💤 idle
   > *"Done. I stopped talking, the mic is off. I can pick up the conversation in text right now without losing a single message."*

---

### 🔍 Scene 3 — Observability & Trust *(~3 min)*

> 🟢 **Status**: Build confidence for IT administrators

**📺 What to show:** Health endpoint, audit trail, session sharing.

**🎙️ Talk track:**

> *"University IT teams ask: 'How do we know what the AI is doing? How do we audit it?' Great question."*

1. 🌐 **Open a new browser tab**, navigate to `https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/realtime/health`
   ```json
   { "realtime_available": true, "mock_mode": false, "voice_enabled": true }
   ```
   > *"This endpoint tells the frontend whether voice is available. If it returns false, the mic button never even appears — there's no broken state to deal with."*

2. 🌐 **Navigate to** `https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/health`
   > *"Full health check — every service, including the Realtime API, has a status entry."*

3. 📜 **Back in the chat**, scroll through the conversation history
   > *"Every voice interaction is logged with `input_modality: voice`. Admins can filter logs to see exactly which queries came through voice, when, and what the agent did. No audio, no PII — just a clean audit trail."*

4. 🔗 **Highlight** that voice and text messages share the same session
   > *"The session ID is identical whether a student types or speaks. That means support staff see a coherent conversation history, not two separate logs."*

```
🔒 Audit Trail:   input_modality: voice  ✅  PII filtered  ✅  No raw audio stored
🔗 Session Link:  voice_session_id === text_session_id  ✅  Unified history
```

---

### 🛡️ Scene 4 — Graceful Degradation *(~2 min)*

> 🟡 **Status**: Show resilience — builds institutional trust

**📺 What to show:** Voice unavailable → text chat continues seamlessly.

**🎙️ Talk track:**

> *"The most important thing about a feature like this is what happens when it doesn't work."*

1. 🔧 **Temporarily disable voice**: In the Azure Container App, set environment variable `VOICE_ENABLED=false` via the portal or:
   ```bash
   az containerapp update --name frontdoor-6wfum6gndxawy-backend --resource-group rg-vvoice \
     --set-env-vars VOICE_ENABLED=false
   ```
   *(If running locally: set `VOICE_ENABLED=false` in `backend/.env` and restart uvicorn)*
2. 🔄 **Refresh the frontend** — mic button is **gone entirely**
   > *"When voice isn't available, we don't show a broken button — we remove it. The student sees a normal, fully functional text chat."*

   ```
   VOICE_ENABLED=false  →  🎤 mic button hidden  →  💬 text chat: fully functional ✅
   ```

3. ⌨️ **Type** a message and get a response
   > *"Text chat is completely unaffected. Voice uses separate WebRTC and WebSocket connections — there's zero coupling to the text pipeline."*

4. ✅ **Re-enable**: Restore `VOICE_ENABLED=true` on the Container App (or in `.env` locally) — mic button reappears

```
Voice OFF:  💬 Text [████████████████████] ✅  🎤 Voice [░░░░░░░░░░] hidden
Voice ON:   💬 Text [████████████████████] ✅  🎤 Voice [████████████████████] ✅
```

> *"Graceful degradation isn't just a buzzword here. It's a constitutional requirement baked into the architecture from day one."*

---

### 🔭 Scene 5 — What's Next *(~2 min)*

> 🟢 **Status**: Close strong — leave them excited

**🎙️ Talk track:**

> *"What you just saw is running live on Azure — connected to Azure OpenAI GPT-4o Realtime API in East US 2. Here's what the path forward looks like."*

```
Current State → Production Hardening:
[████████████████████] Phase 1-3  ✅ Complete — Voice feature merged to main, live on Azure
[████████████░░░░░░░░] Phase 4-6  🟡 In progress
[░░░░░░░░░░░░░░░░░░░░] Phase 7-8  📋 Planned
```

1. 🏭 **Production hardening**: WCAG 2.1 AA audit, screen reader testing with JAWS/NVDA — the Bicep templates in `infra/` already include the full deployment
2. ♿ **Accessibility hardening**: Complete WCAG 2.1 AA audit pass
3. ⚡ **Sub-2-second latency**: Fine-tune Azure Container App scaling + WebRTC transport for optimal response times
4. 📊 **Analytics**: Voice vs. text resolution rate comparison, VAD tuning per environment

> *"The architecture is already live. The tests are green — 435 backend tests pass. Scaling this to production tenants is a **configuration change**, not a code change."*

---

## 🔧 Troubleshooting Table

```
┌─────────────────────────────────────────────────────────────┐
│  🔧  TROUBLESHOOTING QUICK REFERENCE                        │
│  🔴 = Blocking  🟡 = Degraded  🟢 = Self-resolving         │
└─────────────────────────────────────────────────────────────┘
```

| 🚨 Issue | 🔴🟡🟢 | 🔍 Cause | 🛠️ Fix |
|---|---|---|---|
| 🚫 Mic permission denied | 🔴 | Browser blocked microphone access | Click 🔒 lock icon in address bar → Allow Microphone → refresh |
| 🔌 WebSocket fails / `4001` | 🔴 | Ephemeral token expired (TTL ≤ 60 s) | `POST /api/realtime/session` — hook retries automatically |
| 🔌 WebSocket closes `4002` | 🔴 | `session_id` not found | Verify UUID in query params matches a live session; reload |
| 🔇 No audio output | 🔴 | System volume muted / wrong output device | Check system audio; try a headset |
| 🌊 VAD not triggering / false triggers | 🟡 | Background noise | Use headset in quiet room; adjust `REALTIME_VAD_THRESHOLD_MS` in `.env` |
| 🎤 "Voice unavailable" banner | 🟡 | Backend not running or voice disabled | Confirm Container App is running; check `VOICE_ENABLED=true` env var |
| 🚫 `503` on `POST /session` | 🔴 | `VOICE_ENABLED=false` in config | Set `VOICE_ENABLED=true` on Container App → restart revision |
| 🎤 Mic button not shown | 🟡 | `realtime_available: false` from health check | `GET https://frontdoor-6wfum6gndxawy-backend.blackflower-446b9850.eastus2.azurecontainerapps.io/api/realtime/health`; confirm Container App running |
| 📝 Transcript not appearing (user) | 🟡 | Azure OpenAI Realtime API requires explicit `input_audio_transcription` config | Verify `audio.input.transcription: {model: "whisper-1"}` is set in session config (GA nested format in backend `realtime.py`); check that `dc.onopen` sends `session.update` with transcription config (frontend `useVoice.ts`) |
| 📝 Transcript not appearing (agent) | 🟡 | GA API uses different event name than preview docs | Frontend must handle `response.output_audio_transcript.done` (GA) not `response.audio_transcript.done` (preview); fallback: extract from `response.output_item.done` → `item.content[].transcript` |
| 🔴 503 on `/client_secrets` with full config | 🔴 | GA API rejects preview flat fields and `audio.output.transcription` in `/client_secrets` body | Backend has automatic fallback: first request with full config, on 5xx retries without `audio.output.transcription`; preview flat fields (`voice`, `input_audio_transcription`) also cause 500 — use GA nested format |
| 💬 Text chat broken after voice | 🔴 | Should not happen (separate connections) | Hard-reload; file a bug if persists — check `ChatContainer.tsx` state isolation |
| 🔒 WebRTC ICE failure | 🔴 | Azure endpoint/region misconfigured | Verify `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_REALTIME_DEPLOYMENT` in Container App env vars |
| 🔑 `AuthenticationTypeDisabled` | 🔴 | API key auth disabled by Azure policy (`disableLocalAuth: true`) | Use managed identity — Container App must have `Cognitive Services OpenAI User` role on Azure OpenAI resource |
| 🔑 `503` with `auth_type=api-key` | 🔴 | `.env` file baked into Docker image overriding managed identity | Ensure `backend/.dockerignore` excludes `.env`; rebuild with `azd deploy` |
| 🔑 Empty ephemeral token | 🔴 | Token extraction reading wrong response field | Backend must use `data.get("value")` — Azure returns `{"value": "eph_...", "expires_at": ...}` at top level |
| 🌐 Codespaces: API calls fail | 🔴 | `VITE_API_BASE_URL` set to localhost | Clear `VITE_API_BASE_URL` — Vite proxy handles `/api` routing |
| 📦 Container App not starting | 🔴 | Image build failure or missing env vars | `azd deploy --debug`; check Container App logs in Azure Portal |
| 🛑 `azd up` failure | 🔴 | Quota, permissions, or Bicep error | Check `azd` output; verify subscription `ME-MngEnvMCAP262307-segayle-1` and role assignments |
| 🤖 Azure OpenAI quota exceeded | 🔴 | TPM/RPM limit hit on `frontdoor-6wfum6gndxawy-openai` | Check quota in Azure Portal → `rg-vvoice` → OpenAI resource → Deployments |
| 🐌 Cold start delay (first request) | 🟡 | Container App scaling from zero | Wait 10–15 s; send a warm-up request to `/api/health` before the demo |

```
Legend:  🔴 Blocking — demo cannot continue without fix
         🟡 Degraded — demo can proceed with workaround
         🟢 Self-resolving — wait or retry
```

---

## 🏫 EDU Reusable Framing

```
╔══════════════════════════════════════════════════════════════╗
║  🎓  THE PITCH — COPY-PASTE READY TALKING POINTS            ║
╚══════════════════════════════════════════════════════════════╝
```

### 🚪 The "47 Front Doors" Problem

Universities are not monolithic. A typical large institution has separate portals for:
IT support, financial aid, housing, dining, registrar, library, advising, health services, parking, athletics, career services... and more. Students waste hours figuring out **which door to knock on** — and often knock on the wrong one.

```
Before 47 Doors:
🚪IT  🚪FinAid  🚪Housing  🚪Dining  🚪Registrar  🚪Library  🚪Advising  🚪Health ...
Student → "Which door?!" → knocks on all → waits on all → frustrated

After 47 Doors:
              🏠 ONE DOOR
Student → speaks or types → instant routing → right team → resolved ✅
```

> 💬 **The pitch**: *"What if there was one door? One place where any student question — regardless of department — is heard, understood, and routed correctly?"*

### 🤝 The "Trusted Digital Colleague" Narrative

47 Doors is not a chatbot. It is a **digital colleague** — one that:

| 🧠 Capability | 📝 Description |
|---|---|
| 🗺️ Knows the org chart | Routes every query to the right team automatically |
| 📚 Knows the knowledge base | Surfaces relevant articles with RAG-powered search |
| ⚠️ Knows when to escalate | Policy triggers, sensitivity detection, human handoff |
| 💾 Remembers the conversation | Session context across turns **and** modalities |
| 🔒 Never stores what it shouldn't | No raw audio · PII-filtered transcripts · audit-ready logs |

Voice makes this colleague feel **present** — not like filling out a form, but like asking a knowledgeable colleague in the hallway.

### 🌍 Applicable to Any University

This architecture is institution-agnostic. The 3-agent pipeline (`QueryAgent → RouterAgent → ActionAgent`) maps to any university's department taxonomy. With live Azure deployment via `azd up`, any institution can demo it today against real Azure OpenAI — and scale to production deployment after seeing it work for their specific use cases.

> 💬 **The close**: *"You're not buying a chatbot. You're giving every student a trusted digital colleague who is always available, always accurate, and always gets them to the right place — whether they type or talk."*

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📋  Runbook maintained by the 47 Doors engineering team                    ║
║  🐛  Issues? Open a GitHub issue on the repository                          ║
║  ☁️   Azure-first: `azd up` → live on Azure OpenAI (MOCK_MODE=false)         ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

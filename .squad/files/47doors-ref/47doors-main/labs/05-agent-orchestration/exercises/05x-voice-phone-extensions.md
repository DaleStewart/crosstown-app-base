# Exercise 05x: Voice & Phone Extensions (Optional)

**Duration:** 30–45 minutes (stretch goal — complete Labs 00–05 first)  
**Objective:** See your orchestrated agent pipeline respond to voice and phone input using the same architecture you built in Labs 01–05.

---

## Overview

You've built a three-agent pipeline that handles text queries. Now you'll see the **same pipeline** respond to:
1. **Browser voice** — speak into your mic, hear the agent respond
2. **Phone calls** — dial a real number, the agent answers (coach demo)
3. **Live transcripts** — watch a phone call in real-time on the LivePage

The key insight: **voice and phone are input/output modalities, not new agents.** Your QueryAgent, RouterAgent, and ActionAgents work identically regardless of how the student communicates.

---

## Prerequisites

- [ ] Labs 00–05 completed and working
- [ ] Backend running (`uvicorn` or Docker)
- [ ] Frontend running (`npm run dev`)
- [ ] Microphone available (Chrome/Edge recommended)
- [ ] Mock mode is fine — you don't need live Azure credentials

---

## Part 1: Browser Voice (15 minutes)

### Step 1.1: Verify Voice Availability

```bash
curl http://localhost:8000/api/realtime/health
```

**Expected output:**
```json
{"available": true, "mock_mode": true}
```

If `available` is `false`, check that `VOICE_ENABLED=true` in your `.env` file.

### Step 1.2: Understand the Ephemeral Token Pattern

Before voice can work, the frontend needs a short-lived token:

```
Frontend → POST /api/realtime/session → Backend creates ephemeral token (60s TTL) → Frontend uses token for WebRTC
```

**Why 60 seconds?** This is Constitution Principle III (Ephemeral Credentials). The token is single-use and expires quickly, so even if intercepted, it can't be replayed.

Look at `backend/app/api/realtime.py` — find the `create_realtime_session()` function. Notice:
- Token has a TTL field
- In mock mode, the token is `eph_mock_{uuid}`
- In production, it comes from Azure OpenAI's `/openai/v1/realtime/client_secrets` endpoint

### Step 1.3: Try Voice in the Browser

1. Open the frontend at `http://localhost:5173`
2. Find the microphone button (VoiceMicButton component)
3. Click it — grant microphone permission when prompted
4. Ask: **"How do I reset my password?"**
5. Watch the response appear as both text and (in production) spoken audio

**In mock mode:** You'll see the voice state transition (Idle → Connecting → Listening → Processing → Idle) but won't hear audio. The transcript will show a mock response. This is expected—the **architecture flow** is what matters.

### Step 1.4: Trace the Voice Architecture

Open your browser's DevTools (Network tab) and repeat the voice interaction. You should see:

1. `POST /api/realtime/session` — ephemeral token request
2. WebRTC SDP exchange (in production) or mock state transitions
3. The same intent classification and routing you built in Labs 01 and 05

**Checkpoint:** Can you identify which of YOUR agents (from Lab 05) processed the voice query? The answer: all three—QueryAgent classified the intent, RouterAgent selected IT Support, and the ActionAgent (RetrieveAgent) searched the knowledge base.

---

## Part 2: Understanding Phone Architecture (10 minutes)

Phone calls follow a different path because **ACS (Azure Communication Services) can't authenticate directly to Azure OpenAI**. The backend acts as a bridge:

```
Caller → PSTN → ACS → Event Grid webhook
                         ↓
                   POST /api/phone/incoming → Answer call
                         ↓
                   ACS media streaming → WS /ws/acs-media
                         ↓
                   Backend bridge (media_ws.py)
                         ↓
                   Azure OpenAI Realtime API
                         ↓
                   Tool calls → Same 3-agent pipeline
                         ↓
                   Audio response → ACS → Caller
```

### Step 2.1: Read the Bridge Code

Open `backend/app/api/media_ws.py` and find:

1. **`_acs_sender()`** — Reads audio from ACS WebSocket, forwards to OpenAI
2. **`_openai_receiver()`** — Reads from OpenAI, forwards audio back to ACS, executes tool calls
3. **`transcript_bus.publish()`** — Every speech event and tool call is published for the LivePage

**Question to answer:** Why does the bridge run TWO concurrent coroutines? (Hint: audio flows in both directions simultaneously—the caller can speak while the AI is still responding.)

### Step 2.2: Examine the Transcript Bus

Open `backend/app/services/transcript_bus.py`. This is a simple in-memory pub/sub:

- `publish(event)` → pushes to all subscriber queues
- `subscribe()` → returns an async queue that receives events
- Events: `call_started`, `user_speech`, `agent_speech`, `tool_call`, `call_ended`

**Question to answer:** What happens if the frontend disconnects and reconnects? (Hint: it misses events during the gap—the bus has no replay. This is acceptable for a live demo but not for production audit trails.)

### Step 2.3: Explore the LivePage

Open `http://localhost:5173/live` in your browser. This is the audience-facing view for phone demos:

- Dark theme for projector visibility
- Speech bubbles for caller and agent
- Tool call indicators (pulsing cyan pills)
- Auto-scroll to latest event

---

## Part 3: Compare Modalities (5 minutes)

Fill in this comparison table:

| Aspect | Text Chat | Browser Voice | Phone |
|--------|-----------|---------------|-------|
| Input path | HTTP POST /api/chat | WebRTC → Azure OpenAI | PSTN → ACS → WebSocket bridge |
| Authentication | Session cookie | Ephemeral token (60s) | Managed identity (backend) |
| Agent pipeline | QueryAgent → RouterAgent → ActionAgent | _____ | _____ |
| Tools available | 4 tools | _____ | _____ |
| Response format | JSON with markdown | Spoken audio + text transcript | _____ |
| Live audience view | No | No | _____ |
| Mock mode support | Yes | _____ | _____ |

**Key takeaway:** The only differences are the I/O transport layer and authentication model. The intelligence is identical.

---

## Success Criteria

- [ ] Voice health endpoint returns available
- [ ] Understood ephemeral token pattern (can explain why 60s TTL)
- [ ] Tried browser voice (mock mode is fine)
- [ ] Can trace a voice query through all three agents
- [ ] Read the `media_ws.py` bridge code and can explain why two coroutines
- [ ] Explored the LivePage and transcript bus
- [ ] Completed the modality comparison table

---

## Troubleshooting

### Mic button not appearing
- Check `VOICE_ENABLED=true` in `.env`
- Ensure you're using Chrome or Edge (Firefox WebRTC support varies)
- Must be on `localhost` or HTTPS (browser security requirement)

### Voice state stuck on "Connecting"
- In mock mode, this may transition quickly to Idle (no real WebRTC)
- Check browser console for errors
- Refresh the page and try again

### LivePage shows no events
- In mock mode, events only appear if a mock call is triggered
- Check `/api/phone/health` endpoint
- Verify the frontend is connected to the SSE stream (Network tab → EventSource)

---

## Summary

You've seen that voice and phone are **interface layers** on top of the same agent architecture you built in Labs 01–05. The key patterns introduced:

- **Ephemeral tokens** for stateless voice sessions
- **Protocol bridging** for PSTN-to-AI audio relay
- **Pub/sub event bus** for real-time audience display
- **Modality-agnostic agents** — same pipeline, different I/O

---

## Next Steps

Continue to [**Exercise 06a: Local Docker Testing**](../../06-deploy-with-azd/exercises/06a-local-docker.md) to deploy your complete system—voice, phone, and all.

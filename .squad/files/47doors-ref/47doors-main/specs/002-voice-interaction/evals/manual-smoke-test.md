# 🎙️ Voice Feature — Manual Smoke Test Guide

**Feature:** 002-voice-interaction  
**Environment:** Mock Mode (`MOCK_MODE=true`)  
**Last Updated:** 2026-03-13  
**Requested by:** msftsean

---

## Pre-Requisites

Before running any test, verify the following:

| # | Requirement | How to Verify | ✓ |
|---|-------------|---------------|---|
| 1 | Browser: Chrome 90+ or Edge 90+ | `chrome://version` — must be ≥ 90 | ☐ |
| 2 | Microphone permission granted | Browser shows mic icon in address bar | ☐ |
| 3 | Backend running | `curl http://localhost:8000/api/realtime/health` returns `{"status":"ok"}` | ☐ |
| 4 | `MOCK_MODE=true` in backend `.env` | Check `backend/.env`; restart backend if changed | ☐ |
| 5 | `VOICE_ENABLED=true` in backend `.env` | Mic button is visible in the chat UI | ☐ |
| 6 | Frontend running | `http://localhost:3000` loads without errors | ☐ |

---

## Test 1 — Voice Support Request (Mock)

**Goal:** Verify end-to-end voice flow for a password-reset request.

| Step | Action | Expected Outcome | Pass | Fail |
|------|--------|-----------------|------|------|
| 1.1 | Open `http://localhost:3000` in Chrome | Chat UI loads; mic button visible in input area | ☐ | ☐ |
| 1.2 | Click the mic button (🎙️) | Status indicator transitions to **Connecting** | ☐ | ☐ |
| 1.3 | Wait 1–2 seconds | Status indicator transitions to **Listening** | ☐ | ☐ |
| 1.4 | Say: *"I forgot my password and can't log into Canvas"* | User transcript appears in chat | ☐ | ☐ |
| 1.5 | Wait for agent response | Assistant transcript appears; status transitions to **Processing** then **Speaking** | ☐ | ☐ |
| 1.6 | Listen to agent audio | Agent speaks a ticket ID (e.g., `TKT-IT-…`) and KB article guidance | ☐ | ☐ |
| 1.7 | Verify transcript panel | Both user and assistant messages are shown with correct speaker labels | ☐ | ☐ |
| 1.8 | Verify status indicator | After speaking completes, indicator returns to **Idle** or **Listening** | ☐ | ☐ |
| 1.9 | Click mic button again to end session | Session closes cleanly; status returns to **Idle** | ☐ | ☐ |

**Notes / Observations:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## Test 2 — Voice Escalation

**Goal:** Verify the escalation path routes correctly via voice.

| Step | Action | Expected Outcome | Pass | Fail |
|------|--------|-----------------|------|------|
| 2.1 | Click the mic button (🎙️) | Status indicator transitions to **Connecting → Listening** | ☐ | ☐ |
| 2.2 | Say: *"I want to appeal my grade in CS101"* | User transcript appears in chat | ☐ | ☐ |
| 2.3 | Wait for agent response | Agent speaks escalation confirmation including SLA (e.g., "within 5 business days") | ☐ | ☐ |
| 2.4 | Verify transcript | Assistant message references escalation and department (REGISTRAR) | ☐ | ☐ |
| 2.5 | Click mic to end session | Session closes cleanly | ☐ | ☐ |

**Notes / Observations:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## Test 3 — Keyboard Accessibility

**Goal:** Verify voice controls are fully operable via keyboard; no mouse required.

| Step | Action | Expected Outcome | Pass | Fail |
|------|--------|-----------------|------|------|
| 3.1 | Load chat UI, do not click anywhere | Focus is on a default element | ☐ | ☐ |
| 3.2 | Press `Tab` repeatedly until mic button is focused | Mic button has visible focus ring; `aria-label` reads "Start voice input" | ☐ | ☐ |
| 3.3 | Press `Enter` | Voice session starts; status → **Connecting → Listening** | ☐ | ☐ |
| 3.4 | Check `aria-label` on mic button during session | `aria-label` changes to "Stop voice input" | ☐ | ☐ |
| 3.5 | Press `Escape` | Voice session stops; status returns to **Idle** | ☐ | ☐ |
| 3.6 | Check `aria-label` again | `aria-label` reverts to "Start voice input" | ☐ | ☐ |
| 3.7 | Tab away from mic button and back | Focus management is logical; no focus traps | ☐ | ☐ |

**Notes / Observations:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## Test 4 — Graceful Degradation

**Goal:** Verify the UI degrades gracefully when voice is disabled server-side.

| Step | Action | Expected Outcome | Pass | Fail |
|------|--------|-----------------|------|------|
| 4.1 | Open `backend/.env`; set `VOICE_ENABLED=false` | File saved | ☐ | ☐ |
| 4.2 | Restart backend: `cd backend && uvicorn app.main:app --reload` | Server restarts without errors | ☐ | ☐ |
| 4.3 | Hard-refresh `http://localhost:3000` | Page loads without JS errors | ☐ | ☐ |
| 4.4 | Inspect chat input area | Mic button is **not visible** | ☐ | ☐ |
| 4.5 | Type a text message and send | Text chat responds normally; no voice-related errors | ☐ | ☐ |
| 4.6 | Call `GET /api/realtime/health` | Response: `{"status":"disabled"}` or `voice_enabled: false` | ☐ | ☐ |
| 4.7 | Restore `VOICE_ENABLED=true`; restart backend | Mic button reappears after refresh | ☐ | ☐ |

**Notes / Observations:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## Test 5 — Hybrid Session (Text + Voice)

**Goal:** Verify session context is preserved when switching between text and voice modalities.

| Step | Action | Expected Outcome | Pass | Fail |
|------|--------|-----------------|------|------|
| 5.1 | Type and send: *"I'm having trouble with my Canvas account"* | Text response appears in chat; session established | ☐ | ☐ |
| 5.2 | Click the mic button | Voice session starts within the **same** conversation | ☐ | ☐ |
| 5.3 | Say: *"What was the issue I just mentioned?"* | Agent response references Canvas / account context from the prior text message | ☐ | ☐ |
| 5.4 | Verify transcript panel | Both text messages and voice transcripts appear in chronological order | ☐ | ☐ |
| 5.5 | End voice session; send another text message | Text chat continues to work; no session corruption | ☐ | ☐ |

**Notes / Observations:**
```
_____________________________________________________________
_____________________________________________________________
```

---

## Summary Scorecard

| Test | Description | Result |
|------|-------------|--------|
| Test 1 | Voice Support Request (Mock) | ☐ Pass / ☐ Fail |
| Test 2 | Voice Escalation | ☐ Pass / ☐ Fail |
| Test 3 | Keyboard Accessibility | ☐ Pass / ☐ Fail |
| Test 4 | Graceful Degradation | ☐ Pass / ☐ Fail |
| Test 5 | Hybrid Session | ☐ Pass / ☐ Fail |

**Tester:** ________________________  
**Date:** ________________________  
**Build / Commit SHA:** ________________________  
**Overall Result:** ☐ PASS &nbsp;&nbsp; ☐ FAIL (see notes above)

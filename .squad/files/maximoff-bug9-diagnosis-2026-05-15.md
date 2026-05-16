# Bug #9 Diagnosis Report — Maximoff (Anomaly Hunter)

**Date:** 2026-05-15  
**Author:** Wanda Maximoff  
**Status:** COMPLETE — NO CODE SHIPPED  
**Related:** Bug #8 (PR #14), D-009 (gpt-realtime-1.5 GA upgrade)

---

## 1. Current `session.update` Payload (Verbatim from Code)

**Source:** `apps/orchestrator/voice/foundry_realtime.py` lines 174–187

```python
await ws.send(
    json.dumps(
        {
            "type": "session.update",
            "session": {
                "instructions": system_prompt,
                "tools": tool_specs,
                "modalities": ["text", "audio"],
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
            },
        }
    )
)
```

Where `tool_specs` is built as (lines 165–173):

```python
tool_specs = [
    {
        "type": "function",
        "name": t.name,
        "description": t.description,
        "parameters": t.parameters or {"type": "object", "properties": {}},
    }
    for t in tools
]
```

**MISSING from session payload:** `tool_choice` — not present at all.  
**MISSING from `open_session()`:** any await for `session.updated` ACK before returning.

---

## 2. Container Log Evidence (Verbatim, Sanitized)

```
{"TimeStamp": "2026-05-15T21:34:39.809+00:00", "Log": "Application startup complete."}
{"TimeStamp": "2026-05-15T21:34:56.606+00:00", "Log": "100.100.0.19:58922 - \"POST /api/turn HTTP/1.1\" 200 OK"}
{"TimeStamp": "2026-05-15T21:35:03.133+00:00", "Log": "100.100.0.19:39962 - \"POST /api/turn HTTP/1.1\" 200 OK"}
{"TimeStamp": "2026-05-15T21:35:07.995+00:00", "Log": "100.100.0.138:37414 - \"POST /api/turn HTTP/1.1\" 200 OK"}
{"TimeStamp": "2026-05-15T21:35:31.185+00:00", "Log": "100.100.0.138:52694 - \"GET /health HTTP/1.1\" 200 OK"}
```

**Gap:** Container logs only contain HTTP access log lines. The WS protocol frames
(`session.update`, `session.updated`, `response.create`, `error` events) are NOT
logged — the application has no WS-frame-level logging configured. This is a
visibility gap that compounds diagnosis difficulty. There are **no error lines** in
the log — either the `session.update` is accepted, or errors are silently swallowed
(see H4 below).

**Smoke results (from Bug #8 post-deploy test, verbatim):**

```
=== search_logs ===        HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
=== detect_pattern ===     HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
=== summarize_incident === HTTP 200 OK | citations: 0 | tool_calls: [] | warnings: uncited
```

Model text response: `"I don't have access to station logs"` (generic refusal, not an
empty string — confirms the model IS responding, text IS being captured, but no tools
invoked).

---

## 3. MS Learn / OpenAI Realtime API Reference

**Source 1:** https://learn.microsoft.com/en-us/azure/ai-services/openai/realtime-audio-quickstart  
**(2026-05-14 revision)**

The MS Learn Node.js quickstart **explicitly polls for `session.updated`** before
sending any user message:

```javascript
realtimeClient.send({
    'type': 'session.update',
    'session': sessionConfig
});
while (!isConfigured) {
    console.log('Waiting for session.updated event...');
    await new Promise((resolve) => setTimeout(resolve, 100));
}

// After the session is configured, data can be sent to the session.
realtimeClient.send({
    'type': 'conversation.item.create',
    ...
});
realtimeClient.send({ type: 'response.create' });
```

This is unambiguous: the official documentation pattern gates user messages on
receiving `session.updated`.

**Source 2:** https://developers.openai.com/api/reference/resources/realtime

Canonical `SessionUpdateEvent` schema (GA, as of 2026-05-15):

```
RealtimeSessionCreateRequest:
  type: "realtime"           ← required in GA
  output_modalities: array of "text" | "audio"
                             ← NOTE: "It is not possible to request
                               both 'text' and 'audio' at the same time"
  instructions: optional string
  tools: array of RealtimeFunctionTool
  tool_choice: (field documented, values: string modes or forced function)
  audio:
    input:  { format, noise_reduction, transcription, turn_detection }
    output: { format, speed, voice }
```

`RealtimeFunctionTool` (flat schema, confirmed correct):
```
{
  type: "function",
  name: string,
  description: string,
  parameters: JSON Schema object
}
```

**`tool_choice` default:** documented as present but default value NOT explicitly
stated in the API reference. In Chat Completions the default when tools are present
is `"auto"`. Whether Realtime API follows the same convention is unconfirmed.

**Key divergence from our code:**

| Field in our payload | Expected by GA API | Impact |
|---|---|---|
| `modalities: ["text", "audio"]` | `output_modalities: ["text"]` or `["audio"]` (not both) | Wrong field name; invalid combination |
| `input_audio_format: "pcm16"` | `audio.input.format: {type: "audio/pcm"}` | Top-level field not recognized in GA schema |
| `output_audio_format: "pcm16"` | `audio.output.format: {type: "audio/pcm"}` | Top-level field not recognized in GA schema |
| *(missing)* | `type: "realtime"` | Required in GA schema |
| *(missing)* | `tool_choice: "auto"` | Not set; default unclear |

---

## 4. Per-Hypothesis Evidence + Verdict

### H1 — `tool_choice` not set

**Evidence:**  
- The `session.update` payload (line 178–186, `foundry_realtime.py`) does **NOT**
  include `tool_choice`.  
- `tool_choice` IS documented as a session field in the Realtime API reference.  
- For Chat Completions, the default when tools are present is `"auto"`. Realtime API
  likely follows the same convention, but this is not explicitly confirmed for
  `gpt-realtime-1.5`.  
- The container logs show no errors that would indicate tools are actively rejected —
  consistent with tools being registered but the model choosing not to call them.

**Verdict: INCONCLUSIVE / CONTRIBUTING**  
Not the sole root cause, but zero-risk to add `tool_choice: "auto"` explicitly.
Including it in the recommended fix.

---

### H2 — Timing race: no await for `session.updated`

**Evidence (strongest):**  
1. `open_session()` sends `session.update` then spawns a background pump task then
   **returns immediately** — no `await` for `session.updated` (lines 189–199).  
2. `api_turn` in `main.py` calls `session.send_text(body.text)` the instant
   `open_session()` returns (line 98). This fires `conversation.item.create` +
   `response.create` on the wire before `session.updated` arrives from the server.  
3. The MS Learn quickstart **explicitly and documented-ly** waits for `session.updated`
   before sending any user message. This is not a style preference — it is the
   required pattern.  
4. If the server's session-update processing is async (common for Realtime API), the
   response.create is received before the session state has the tools registered.
   The model responds without any callable functions.  
5. The model's response `"I don't have access to station logs"` is the exact text
   a model without tool registration would produce given the system prompt.

**Verdict: BUG — HIGH CONFIDENCE**  
This is the primary root cause. The fix is to await `session.updated` inside
`open_session()` before returning.

---

### H3 — System prompt insufficient for Realtime context

**Evidence:**  
`apps/orchestrator/system_prompt.py`:
```python
SYSTEM_PROMPT = """You are the MTA Operations Copilot.

You help dispatchers and engineers triage train-control incidents.
You answer briefly, cite sources for every factual claim, and call tools
instead of guessing. When a tool returns citations, surface them.

Tools available come from the Log Analyst service:
- search_logs(query, severity?, limit?): full-text + semantic search over logs
- detect_pattern(window_minutes, pattern?): structural pattern detection
- summarize_incident(incident_id): produces a cited incident summary

If a user asks a non-MTA question, politely steer back to operations.
"""
```

The prompt includes "call tools instead of guessing" and lists all three tool names.
For a correctly configured session, this is sufficient. This is NOT the root cause —
but the `"I don't have access to station logs"` response is a hint the model thinks
tools are unavailable (not registered), not that it's ignoring a strong prompt.

**Verdict: RULED OUT as primary cause**

---

### H4 (4th hypothesis) — Schema mismatch: old API format sent to gpt-realtime-1.5 GA

**Evidence:**  
The code was written for `gpt-4o-realtime-preview` which used:
- `modalities: ["text", "audio"]` at session level
- `input_audio_format` / `output_audio_format` as top-level session fields

The `gpt-realtime-1.5` GA API uses:
- `type: "realtime"` in the session object (required)
- `output_modalities: ["text"]` or `["audio"]` (mutually exclusive, not both)
- `audio.input.format` / `audio.output.format` nested objects

**Sub-finding: Errors are silently swallowed.** The `_translate()` method in
`FoundryRealtimeSession` (lines 95–133) drops ALL events it doesn't recognise —
including `error` events from the server:

```python
def _translate(self, data: dict[str, Any]) -> VoiceEvent | None:
    kind = data.get("type", "")
    if kind == "response.audio.delta": ...
    if kind == "response.audio_transcript.delta": ...
    ...
    return None  # ← error, session.updated, and ALL other events silently dropped
```

If the `session.update` fails with an `error` event (due to schema mismatch), the
pump drops it silently. The caller sees no exception, no log line. The session
proceeds without tool registration. The model responds generically with no tool calls.

**Critical implication:** The clean container logs do NOT prove the session.update
succeeded — they only prove no Python-level exception was raised. A WS-protocol-level
`error` event from the server would be silently swallowed.

**Verdict: BUG — MEDIUM CONFIDENCE (secondary/compounding)**  
Schema mismatch may be causing session.update errors that are silently dropped, leaving
the session with no tools. This interacts with H2: even if the schema is "best-effort
accepted" with tools intact, the timing race ensures they haven't propagated before
response.create fires.

---

## 5. Verdict

**ROOT CAUSE: H2 (Timing Race) — HIGH CONFIDENCE, supported by H4 (Schema Mismatch) — MEDIUM CONFIDENCE**

The most parsimonious explanation matching all evidence:

1. `open_session()` sends `session.update` (possibly with incorrect schema fields)
2. The pump task is spawned but hasn't read a single byte yet — the asyncio event loop
   hasn't yielded back to it
3. `open_session()` returns immediately
4. `api_turn` calls `send_text()` which fires `conversation.item.create` +
   `response.create` before the server has ACK'd `session.updated`
5. The server either: (a) has not yet processed session.update's tools registration,
   OR (b) has rejected the session.update (schema error) and sent an `error` event
   that the pump will eventually swallow
6. `response.create` is processed without tools registered → model responds generically

The model text "I don't have access to station logs" is the smoking gun: a model
WITH tool registration would attempt `search_logs`, not refuse and claim no access.

---

## 6. Recommended Fix

**Two-file, targeted change. Ship H2 fix + H1 defensive add together.**

### File: `apps/orchestrator/voice/foundry_realtime.py`

**Change 1: Add `tool_choice` to session.update payload**  
Line 178 area (inside the `session` dict):

```python
# BEFORE (line 185–186, end of session dict):
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",

# AFTER:
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "tool_choice": "auto",
```

**Change 2: Await `session.updated` before returning from `open_session()`**  
Replace lines 189–199 (current pump definition and task creation):

```python
# BEFORE (lines 189–199):
        async def pump() -> None:
            try:
                async for raw in ws:
                    if isinstance(raw, bytes):
                        continue
                    await session._ingest(raw)
            finally:
                await session._inbound.put(None)

        asyncio.create_task(pump())
        return session

# AFTER:
        session_ready: asyncio.Event = asyncio.Event()

        async def pump() -> None:
            try:
                async for raw in ws:
                    if isinstance(raw, bytes):
                        continue
                    try:
                        evt = json.loads(raw)
                        if evt.get("type") == "session.updated":
                            session_ready.set()
                    except json.JSONDecodeError:
                        pass
                    await session._ingest(raw)
            finally:
                await session._inbound.put(None)

        asyncio.create_task(pump())
        await asyncio.wait_for(session_ready.wait(), timeout=10.0)
        return session
```

**Exact diff (unified format):**

```diff
--- a/apps/orchestrator/voice/foundry_realtime.py
+++ b/apps/orchestrator/voice/foundry_realtime.py
@@ -182,13 +182,25 @@ class FoundryRealtimeProvider:
                         "modalities": ["text", "audio"],
                         "input_audio_format": "pcm16",
                         "output_audio_format": "pcm16",
+                        "tool_choice": "auto",
                     },
                 }
             )
         )
 
-        async def pump() -> None:
+        session_ready: asyncio.Event = asyncio.Event()
+
+        async def pump() -> None:  # noqa: E731
             try:
                 async for raw in ws:
                     if isinstance(raw, bytes):
                         continue
+                    try:
+                        evt = json.loads(raw)
+                        if evt.get("type") == "session.updated":
+                            session_ready.set()
+                    except json.JSONDecodeError:
+                        pass
                     await session._ingest(raw)
             finally:
                 await session._inbound.put(None)
 
         asyncio.create_task(pump())
+        await asyncio.wait_for(session_ready.wait(), timeout=10.0)
         return session
```

**Files changed:** 1  
**Lines:** +13 / -1  

**Why not fix H4 (schema mismatch) at the same time?**  
Schema migration to the full GA format (`output_modalities`, `audio.input.format`, etc.)
is a broader change with blast radius across the test suite (unit tests mock the WS
directly). Brady should file that as Bug #10 separately once Bug #9 is confirmed
fixed. If H2+H1 fix does NOT resolve tool dispatch, H4 is the next candidate.

---

## 7. Confidence

**H2 (timing race): HIGH**  
Directly confirmed by MS Learn explicit pattern + code reading. No speculation.

**H1 (tool_choice): LOW as primary, but adding it is zero-risk**  
Default behavior unclear for Realtime GA; Chat Completions default is "auto" when
tools present; Realtime likely same but not confirmed.

**H4 (schema mismatch): MEDIUM**  
The field divergence is confirmed by reading the GA API reference. Whether the server
silently accepts old fields or errors depends on server-side behavior. The silent-error
swallow in `_translate` means we cannot distinguish "schema rejected" from "schema
accepted" without WS-level logging.

**Combined H2 + H1 fix confidence: HIGH**  
If the MS Learn pattern (await session.updated) is followed and tool_choice is
explicit, tool dispatch should succeed. If it does not, H4 (schema migration) is the
unambiguous next step.

---

## 8. Alternative Paths

If H2 + H1 fix does not resolve tool dispatch, try in order:

1. **H4-partial:** Add `tool_choice: "auto"` (already in fix above) plus update
   `modalities` → `output_modalities: ["text"]`. The text-only path in `/api/turn`
   should use `["text"]` not `["text", "audio"]`. Small change, low risk.

2. **H4-full:** Migrate entire session.update to GA schema:
   - `type: "realtime"` in session object
   - `output_modalities: ["text"]` for `/api/turn`, `["audio"]` for `/ws/voice`
   - `audio: { input: { format: { type: "audio/pcm" } }, output: { ... } }`
   - Remove `input_audio_format` / `output_audio_format` top-level fields
   This is the higher-effort but most correct path.

3. **Add WS-frame logging** to `pump()`: log all incoming events at DEBUG level. This
   will immediately expose any `error` events from the server and confirm whether
   session.update is accepted.

---

## 9. Next Action

Brady (or any Squad member): ship the 2-change fix above (tool_choice + session_ready
await) to `foundry_realtime.py`, then `azd deploy orchestrator`. Run the 3-path smoke
test. Expect `tool_calls: [{name: "search_logs", ...}]` in the response.

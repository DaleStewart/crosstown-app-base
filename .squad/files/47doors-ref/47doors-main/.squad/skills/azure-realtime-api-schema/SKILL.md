# Skill: Azure OpenAI Realtime API — Schema per Endpoint

## When to use

You are configuring a `session.update` for Azure OpenAI's Realtime API and need to know the correct field shape, OR you are debugging silent transcription failures / `unknown_parameter` errors on a realtime WebSocket.

## Key fact

**The Azure OpenAI Realtime API has two endpoints with two different `session.update` schemas. They are NOT interchangeable.**

### Endpoint A — direct WebSocket (server-to-server, e.g. ACS phone bridge)

URL pattern:
```
wss://<resource>.openai.azure.com/openai/realtime?api-version=2025-04-01-preview&deployment=<name>
```

Use **FLAT** session-level fields:

```python
{
  "type": "session.update",
  "session": {
    "instructions": "...",
    "voice": "alloy",
    "input_audio_format":  "pcm16",
    "output_audio_format": "pcm16",
    "input_audio_transcription": {"model": "whisper-1"},
    "turn_detection": {"type": "server_vad", ...},
    "tools": [...]
  }
}
```

**Do NOT** send a nested `audio: { input: {...}, output: {...} }` block. Azure rejects it with:

```
invalid_request_error / unknown_parameter
"Unknown parameter: 'session.audio'."  param: 'session.audio'
```

### Endpoint B — WebRTC calls (browser client)

URL pattern:
```
https://<resource>.openai.azure.com/openai/v1/realtime/calls
```

Use **NESTED** `audio` block:

```python
{
  "type": "session.update",
  "session": {
    "instructions": "...",
    "audio": {
      "input":  {"format": "pcm16", "transcription": {"model": "whisper-1"}},
      "output": {"format": "pcm16", "voice": "alloy", "transcription": {"model": "whisper-1"}}
    },
    "turn_detection": {"type": "server_vad", ...},
    "tools": [...]
  }
}
```

Here the flat `input_audio_transcription` / `input_audio_format` fields are rejected as unknown.

## Debugging checklist — silent transcript failure

Symptoms: agent audio works, agent transcript (`response.audio_transcript.done`) works, but **caller transcript is empty**.

1. Check container logs for `unknown_parameter` on a `session.update`-related message. Azure reports the error but the socket stays open.
2. Confirm which endpoint you're using (direct WS vs WebRTC calls).
3. Match the schema to the endpoint per the table above.
4. After fixing, confirm `conversation.item.input_audio_transcription.delta` and `.completed` events are arriving.

## Incidental gotcha — `websockets` library

Newer `websockets` versions removed `ClientConnection.closed`. Code like `if openai_ws and not openai_ws.closed:` raises `AttributeError` at teardown. Replace with:

```python
if openai_ws is not None:
    try:
        await openai_ws.close()
    except Exception:
        pass
```

## References

- Reproduced and fixed in `backend/app/api/media_ws.py` (47doors repo).
- Decision: `.squad/decisions/inbox/tank-realtime-api-schema.md`.

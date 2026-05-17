## What

Re-enables user speech transcription in the voice loop so both sides of the conversation are visible — not just assistant replies.

## Why

PR #20 dropped `input_audio_transcription` from `session.update` because it caused a 10-second timeout on the first deploy attempt. That was the right call to unblock voice playback, but it left the user side silent. This PR restores it safely.

## How it works

**Two-phase session.update strategy:**
1. **Phase 1** (required): known-safe `session.update` with `instructions`, `tools`, `tool_choice`, `output_modalities`. Waits for `session.updated` ACK.
2. **Phase 2** (conditional): a second `session.update` with the GA nested format `audio.input.transcription.model`. Only fires when `AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT` is explicitly set to a valid deployment name. **DANGER:** Azure OpenAI closes the WebSocket if the deployment name is invalid — this is NOT a soft error. Disabled by default (`""`).

This is safe because by the time Phase 2 fires, `session_ready` is already set and `session_error` is no longer checked.

## Also includes (PR #20 orchestrator fixes not yet in main)

- `FoundryRealtimeSession.commit_audio()` — sends `input_audio_buffer.commit` + `response.create` so the model processes speech
- Pump error capture — `error` events unblock `session_ready` and raise immediately (no 10-second timeout hang)
- `orchestrator.py` stop handler — calls `commit_audio()` and stays in loop (no `break`); WS close from client disconnect exits cleanly

## Client event contract

```json
{"type": "transcript_delta", "role": "user", "text": "...", "final": false}
{"type": "transcript_delta", "role": "user", "text": "...", "final": true}
```

Same shape as assistant transcript events — `role` distinguishes the speaker. Parker's frontend PR (#21) renders on this contract.

## New configuration

`AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT` (default: `""` — disabled)
- Azure OpenAI requires an existing deployment name per [MS Learn docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/realtime-audio-reference)
- OpenAI (non-Azure) accepts `whisper-1` directly
- Set to empty string (default) to disable transcription entirely (voice loop unaffected)

## Changes

| File | Change |
|------|--------|
| `voice/foundry_realtime.py` | `commit_audio()`; pump error capture; phase-2 transcription update; `_translate` handlers for `.delta` and `.failed` |
| `agent/orchestrator.py` | stop handler: commit_audio + no break |
| `settings.py` | `azure_openai_transcription_deployment` field |
| `voice/factory.py` | pass `transcription_deployment` to provider |
| `tests/test_foundry_realtime.py` | 14 new tests covering all `_translate` paths |

## Validation

- ruff: clean
- mypy --strict: 20 files, no issues
- pytest: 25/25 pass (14 new in test_foundry_realtime.py)

## Coordination

Parker (PR #21) is rendering `transcript_delta` events with `role === 'user'`. The event name and payload shape are locked — no changes needed on his end.

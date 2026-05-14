# Voice

Two providers behind one orchestrator interface, toggled by a single env var:

```
VOICE_PROVIDER=foundry_realtime   # primary (default)
VOICE_PROVIDER=speech_services    # fallback
```

The frontend is provider-agnostic — it streams microphone audio to the orchestrator over WebSocket and receives transcripts + audio back. Switching providers is a server-side env flip + redeploy; no frontend change.

## Primary: Foundry Realtime (gpt-4o-realtime-preview)

**Why it's the default:** single round-trip for STT + reasoning + TTS, lowest latency, native interruption handling.

**How it works in this repo:**
- The orchestrator opens a WebSocket to Foundry's realtime endpoint using the user-assigned managed identity (no keys).
- The Foundry session is instructed with the orchestrator's system prompt plus tool definitions for routing to specialists.
- The orchestrator acts as a relay: client frames → Foundry, Foundry frames → client.
- When Foundry emits a tool call, the orchestrator dispatches it to the specialist (HTTP), gets a response with citations, and returns it back into the Foundry session.

**Required Bicep:**
- A `gpt-4o-realtime-preview` model deployment under the Foundry/AOAI account.
- `Cognitive Services User` role on the AOAI account for the UAMI.

**Env vars consumed:**
- `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`
- `AZURE_OPENAI_REALTIME_DEPLOYMENT` (default `gpt-4o-realtime-preview`)

## Fallback: Azure Speech Services (STT + TTS)

**When to use:**
- Regions or subscriptions where `gpt-4o-realtime-preview` is unavailable.
- Audio compliance requirements that mandate the Speech-Services SLA path.
- Demos where you want to use a custom voice or pronunciation dictionary.

**How it works:**
- Orchestrator runs three loops in parallel per turn:
  1. STT (continuous recognition) on the user's audio stream.
  2. Chat completions against `gpt-4.1` for routing + composition.
  3. TTS on the composed reply, streamed back to the frontend.
- The orchestrator still dispatches tool calls to the Log Analyst over HTTP — that part is unchanged.

**Required Bicep:**
- `Microsoft.CognitiveServices/accounts` of kind `SpeechServices`.
- `Cognitive Services Speech User` role on the Speech account for the UAMI.

**Env vars consumed:**
- `AZURE_SPEECH_ENDPOINT`
- `AZURE_SPEECH_REGION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT` (default `gpt-4.1`)

## Switching providers

```bash
# Locally
echo "VOICE_PROVIDER=speech_services" >> .env

# In a deployed ACA env
az containerapp update -n <orchestrator> -g <rg> \
  --set-env-vars VOICE_PROVIDER=speech_services
```

## Push-to-talk vs continuous
The frontend ships with **push-to-talk** as the default to keep demos clean and to prevent accidental wake-ups. To enable continuous mode, set `VITE_VOICE_MODE=continuous` at build time. (Both modes work with either provider.)

## Troubleshooting
| Symptom | Likely cause | Fix |
|---|---|---|
| WS connects then drops in <1s | Realtime model not deployed in the chosen region | Check Foundry deployments; consider East US 2 or Sweden Central |
| Audio plays but no transcript | STT path failing | Flip `VOICE_PROVIDER=speech_services` and re-test |
| "AccessDenied" on first call | UAMI role propagation delay | Wait 2–3 minutes after `azd up`, then retry |
| Garbled audio on safari | Browser sample rate mismatch | Use Chrome/Edge for the demo |

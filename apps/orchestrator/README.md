# MTA Orchestrator

FastAPI WebSocket service that brokers voice turns between the frontend and the
configured voice provider (Foundry Realtime or Azure Speech Services), dispatches
tool calls to the Log Analyst, and persists conversation turns to Cosmos.

## Endpoints
- `GET  /health`  — provider + status snapshot
- `GET  /api/conversations/{id}` — transcript replay
- `WS   /ws/voice` — voice/text relay

## Run
```bash
uv venv && uv pip install -e ".[dev]"
uvicorn main:app --reload --port 8000
```

Set `VOICE_PROVIDER` to either `foundry_realtime` (default) or `speech_services`.

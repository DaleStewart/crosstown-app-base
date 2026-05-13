# MTA Orchestrator

FastAPI WebSocket service that brokers voice turns between the frontend and the
configured voice provider (Foundry Realtime or Azure Speech Services), dispatches
tool calls to the Log Analyst, and persists conversation turns to Cosmos.

## Endpoints

| Method | Path | What |
|---|---|---|
| `GET`  | `/health` | Provider + status snapshot |
| `GET`  | `/api/conversations/{id}` | Transcript replay (Cosmos) |
| `POST` | `/api/turn` | Text-only single-turn (used by evals + red team + non-voice clients) |
| `WS`   | `/ws/voice` | Voice/text relay |

### `/api/turn` request/response

```http
POST /api/turn
Content-Type: application/json

{ "text": "anything wrong on L2?" }
```

```json
{
  "text": "Doors-held cluster on L2 around Beacon...",
  "citations": [{"type":"log","id":"L-000123","snippet":"doors.held sample"}],
  "tool_calls": [{"name":"search_logs","arguments":{"query":"doors held L2"},"call_id":"c1"}],
  "warnings": []
}
```

Reuses the same voice-provider session + tool-routing path as the WebSocket flow, so the citation contract and routing behavior are identical. `tool_calls` is what the orchestrator eval grades against for routing correctness. If no citations and no `uncited` warning, the response is auto-tagged `"uncited"`.

## Run
```bash
uv venv && uv pip install -e ".[dev]"
uvicorn main:app --reload --port 8000
```

Set `VOICE_PROVIDER` to either `foundry_realtime` (default) or `speech_services`.

## Related gates

- Citation eval — `evals/runner.py` (tool-layer)
- **Orchestrator eval — `evals/orchestrator_runner.py` (grades `/api/turn`)**
- Red team — `redteam/runner.py` (grades `/api/turn`)
- Foundry evaluators (optional) — `evals/runner.py --with-foundry`

Thresholds and the recalibration protocol live in `evals/calibration.md`.

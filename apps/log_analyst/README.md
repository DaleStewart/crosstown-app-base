# Log Analyst

Python 3.11 FastAPI microservice for the MTA AI Hackathon accelerator. Exposes three
"tools" that the orchestrator invokes over HTTP. Every tool response includes a
`citations` array; missing citations surface as `warnings: ["uncited"]` so the
eval gate can fail loudly.

## Endpoints

| Method | Path                          | Description                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/health`                     | Liveness probe                           |
| GET    | `/tools`                      | List registered tool descriptors         |
| POST   | `/tools/search_logs`          | Hybrid search over `mta-logs`            |
| POST   | `/tools/detect_pattern`       | Match known signatures in a time window  |
| POST   | `/tools/summarize_incident`   | LLM summary of a Cosmos incident         |

All POST responses share the shape:

```json
{
  "tool": "search_logs",
  "result": { },
  "citations": [{"type": "log", "id": "L-000123", "snippet": "..."}],
  "trace_id": "uuid"
}
```

## Tools

### `search_logs(query, time_range)`
Hybrid Azure AI Search against `AZURE_SEARCH_INDEX_LOGS`. Returns top-10 hits.
Each hit becomes one citation (`type=log`).

### `detect_pattern(log_id, window_minutes=60)`
Fetches the seed log, pulls all logs on the same `line` within the window, and
matches three signatures replicated from `data/generate_mock_data.py`:

| Signature | Event types | Runbook |
|---|---|---|
| `cascading_doors_then_dwell` | `doors.held`, `train.dwell`, `comms.jitter` | `RB-01-doors-held` |
| `interlock_pre_emergency`    | `interlock.fault`, `speed.restriction`, `emergency.brake` | `RB-05-interlock-fault` |
| `shunt_then_power_trip`      | `trackcircuit.shunt`, `loss.of.shunt`, `power.trip` | `RB-07-shunt-then-trip` |

A signature matches when every event type appears at least once in the window
(any order). Zero matches → `warnings: ["no_patterns"]` and the seed log is still
cited.

### `summarize_incident(incident_id)`
Reads the incident doc from Cosmos (`AZURE_COSMOS_*`, partition key `/incidentId`)
and asks `gpt-4o` (`AZURE_OPENAI_CHAT_DEPLOYMENT`) to produce a two-sentence
summary plus a recommended runbook. Both the incident and the runbook are cited.

## Run locally

```powershell
cd apps\log_analyst
uv venv
uv pip install -e ".[dev]"
.\.venv\Scripts\Activate.ps1
uvicorn main:app --port 8001 --reload
```

## Validate

```powershell
ruff check .
mypy --strict .
pytest -q
```

## Authentication

All Azure SDK clients use `DefaultAzureCredential` — no keys. Set
`APPLICATIONINSIGHTS_CONNECTION_STRING` to enable OpenTelemetry export.

## Docker

```powershell
docker build -t mta-log-analyst .
docker run --rm -p 8001:8001 mta-log-analyst
```

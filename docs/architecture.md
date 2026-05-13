# Architecture

The MTA AI Hackathon accelerator is an opt-in Track 2 scaffolding. It deploys to one Azure subscription via `azd up` and demonstrates a **voice → orchestrator → specialist → cited reply** loop using a single specialist agent (Log Analyst).

## Services (Hour-1 skeleton)

| Service | Tech | ACA ingress | Responsibility |
|---|---|---|---|
| `frontend` | Vite + React + shadcn/ui | external :80 | Push-to-talk, transcript, tool-call/citation panel |
| `orchestrator` | Python 3.11 + FastAPI | external :8000 (WebSocket) | Routes turns, calls specialists, owns the conversation memory window, brokers voice |
| `log-analyst` | Python 3.11 + FastAPI | internal :8001 | Three tools (`search_logs`, `detect_pattern`, `summarize_incident`); every response carries citations |

## Azure resources (Bicep-provisioned)

- **Azure AI Foundry** — hub + project + AOAI model deployments (`gpt-4o`, `gpt-4o-realtime-preview`)
- **Azure AI Search** (Basic, semantic search on) — two indexes: `mta-logs`, `mta-runbooks`
- **Cosmos DB for NoSQL** (Serverless) — `incidents` + `conversations` containers
- **Azure Speech Services** (S0) — voice fallback when `VOICE_PROVIDER=speech_services`
- **Postgres Flexible Server** — provisioned **idle**; Extension 09 wires it in
- **ACR** + **Container Apps environment** + **3 Container Apps**
- **Key Vault** (RBAC), **Log Analytics + App Insights**
- **User-Assigned Managed Identity** — used by all three apps for ACR pull + data-plane access

## Identity & secrets
- Single user-assigned managed identity attached to all three Container Apps
- No keys in code or in env. All data-plane access uses `DefaultAzureCredential` → the UAMI
- Role assignments live in `infra/modules/roleAssignments.bicep`
- The user running `azd up` is granted equivalent dev-time roles for local debugging

## Voice flow

```mermaid
flowchart LR
  FE[Frontend push-to-talk] -- WSS --> ORC[Orchestrator]
  ORC -- realtime WS --> FRT[Foundry Realtime gpt-4o-realtime-preview]
  ORC -. fallback .-> SPC[Azure Speech STT+TTS]
  ORC -- HTTP --> LA[Log Analyst]
  LA --> SRCH[(AI Search)]
  LA --> COS[(Cosmos)]
  ORC --> COS
```

The voice path is selected by `VOICE_PROVIDER` env var. See [voice.md](voice.md) for details.

## Data flow

1. User speaks → frontend streams audio over WSS to orchestrator
2. Orchestrator forwards to voice provider, receives transcripts in real time
3. Orchestrator routes the user turn to the Log Analyst over HTTP
4. Log Analyst calls one or more tools; each tool result carries `citations[]`
5. Orchestrator composes the final reply, persists the turn to Cosmos, and returns voice/text to the frontend
6. Citations are surfaced in the frontend's tool-call panel

## Observability
- OpenTelemetry via `azure-monitor-opentelemetry` in each Python service
- App Insights connection string injected via env (Key Vault for secret form)
- Foundry tracing enabled on every agent turn

## Extension points
- New specialists: copy `apps/log_analyst/` to `apps/<name>/`, add Bicep call in `main.bicep`, register routing in orchestrator
- New tools: add to `apps/<specialist>/tools/`, register in the tool router
- New grounding: drop a corpus under `data/<your_corpus>/`, extend `scripts/load_search_index.py`

See [docs/use-case-map.md](use-case-map.md) for which extension fits which submitted use case.

# Crosstown — MTA AI Agent Hackathon (Track 2)

> Reference stack for a multi-specialist transit copilot. Frontend → orchestrator → specialist agents over WebSocket + tool calling, with a separate judging app for coaches.

## Live demos

- **Rider copilot (text + voice):** https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/
- **Coach judging app:** https://mango-hill-0ee13cb0f.7.azurestaticapps.net/

## Architecture (60-second tour)

```
┌─────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│ Frontend    │────→│ Orchestrator         │────→│ Log Analyst      │
│ (React)     │  WS │ (FastAPI, Realtime)  │ HTTP│ (FastAPI)        │
│             │     │ • Session mgmt       │     │ • search_logs    │
└─────────────┘     │ • Voice relay        │     │ • detect_pattern │
                    │ • Tool routing       │     │ • summarize      │
                    └──────────────────────┘     └──────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
      ┌──────────────────┐         ┌────────────────┐
      │ Service Advisor  │         │ Azure AI Search│
      │ (FastAPI)        │         │ Cosmos DB      │
      │ • get_disruption │         │ (citations)    │
      │ • find_route     │         └────────────────┘
      └──────────────────┘
```

**Flow:** User (text or voice) → Frontend → Orchestrator (routes to specialist) → Specialist (calls tools with citations) → Composed response back to user. All tool calls are cited.

## Repo layout

- `apps/frontend/` — React/Vite chat UI (push-to-talk, streaming, tool-call panel)
- `apps/orchestrator/` — FastAPI WebSocket relay + Azure AI Foundry Realtime bridge
- `apps/log_analyst/`, `apps/service_advisor/` — Tool-call specialists (Python)
- `apps/judging/` — Static Web App + Functions for hackathon coaches
- `docs/` — architecture, voice loop, evals, red team, use-case mapping
- `infra/` — Bicep + Azure Developer CLI config
- `evals/` — citation gate, orchestrator gate, evaluator logic
- `redteam/` — adversarial scenario library

## Run it locally

**Frontend:**
```bash
cd apps/frontend
npm install
npm run dev          # Vite dev server at http://localhost:5173
```

**Orchestrator** (requires Python 3.11+, Azure CLI auth, Foundry credentials):
```bash
cd apps/orchestrator
pip install -e ".[dev]"
python -m uvicorn main:app --reload --port 8000
```

**Full stack (recommended):**
```bash
azd auth login
azd up               # ~15–20 min; provisions everything and deploys
# Opens the live frontend URL
```

## Status as of 2026-05-18

- ✅ Text input: stable end-to-end (orchestrator → specialists → citations)
- ✅ Service Disruption Advisor: routes for L1/L2/L3 queries
- ✅ Judging app: GitHub OAuth gate, /api/teams instrumented
- ✅ Voice input: end-to-end working; assistant reliably replies (brief overlap possible on rapid follow-up)
- Latest commit: `8adf29e` (fix: disable PR #45 auto-cancel so AI reliably talks back)

## Demo win condition (Tuesday, 19-May)

**Minimum:** Text input → specialist tool calls → citations in tool-call panel. This wins on Agent Architecture & Foundry Use (30% judging weight).

**Stretch:** Voice input working. Not a blocker if text is solid.

## For hackathon coaches

👉 See [COACHES.md](./COACHES.md).

---

## Extensions & use cases

This is **opt-in scaffolding**. Teams fork and extend toward their use case. See [docs/use-case-map.md](docs/use-case-map.md) for how submitted use cases map to extensions:

- Add a Health Analyst specialist
- Swap the grounding corpus
- Wire a legacy .NET API as a tool
- Custom evals for your domain
- [... and 5 more](docs/extensions/)

## Safety gates (CI)

Four gates run in `.github/workflows/`:

| Gate | Threshold |
|---|---|
| **Citation eval** | ≤5% uncited turns |
| **Orchestrator eval** | 0% scenario failures |
| **Foundry evaluators** | each score ≥3.0/5 |
| **Red team** | 0 high/critical; ≤10% overall |

All run hermetically offline (cassettes) and switch to live mode with a single env var. See [docs/evals.md](docs/evals.md) and [docs/redteam.md](docs/redteam.md).

---

## 📚 Docs

- [docs/architecture.md](docs/architecture.md) — services, data flow, security
- [docs/voice.md](docs/voice.md) — Foundry Realtime + Speech Services fallback
- [docs/evals.md](docs/evals.md) — citation + orchestrator + evaluator gates
- [docs/redteam.md](docs/redteam.md) — adversarial scenarios
- [docs/use-case-map.md](docs/use-case-map.md) — your use case → extension

## Notes

- **Mock data only.** Rail lines fictional (L1/L2/L3). No real MTA systems, employees, or schedules.
- **No secrets in repo.** `.env.example` only; secrets via Key Vault + managed identity.
- **Track 2 (code).** Copilot Studio teams → Track 1 coaches.

🚇 _Built for the NYCMTA AI Hackathon · May 2026_ 🚇

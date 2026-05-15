# Copilot instructions — mta-ai-hackathon

Opt-in scaffolding for the NYCMTA AI Hackathon Track 2 (App Modernization). Hour-1 skeleton: **voice → orchestrator → specialist → cited reply**. All data under `data/` is synthetic; rail lines `L1/L2/L3` are fictional.

## Repo layout

- `apps/orchestrator/` — Python 3.11 FastAPI; WebSocket voice relay + `POST /api/turn` (text). Brokers Foundry Realtime or Azure Speech, dispatches tools to log-analyst, persists turns to Cosmos.
- `apps/log_analyst/` — Python 3.11 FastAPI; three tools at `POST /tools/{search_logs,detect_pattern,summarize_incident}`. Internal-only ACA ingress.
- `apps/frontend/` — Vite + React + Tailwind + shadcn/ui; push-to-talk UI.
- `infra/` — Bicep (`main.bicep` + `modules/`). `azd up` provisions Foundry, AI Search, Cosmos, Speech, ACR, ACA env + 3 apps, Key Vault, App Insights, UAMI, idle Postgres.
- `evals/` — citation gate (`runner.py`) + orchestrator gate (`orchestrator_runner.py`) + optional Foundry evaluators. Scenarios + cassettes for hermetic offline runs.
- `redteam/` — 8 adversarial families, same offline/live model as evals.
- `data/`, `scripts/load_search_index.*` — mock corpus + index loader (runs as azd `postprovision` hook).
- `docs/extensions/01..09` — exercises forking teams pick from; each ships failing tests that teams make pass.

## Build / test / lint

Python services (run from `apps/orchestrator` or `apps/log_analyst`):

```bash
pip install -e ".[dev]"
ruff check .
mypy --strict .         # both services are strict-mypy clean — keep them that way
pytest -q
pytest tests/test_foo.py::test_bar -q   # single test
```

Frontend (`apps/frontend`):

```bash
npm ci
npm run lint
npm run typecheck
npm test -- --run                       # vitest, single run
npm test -- --run path/to/file.test.tsx # single file
npm run build                           # tsc -b && vite build
```

Eval gates (`evals/`, hermetic by default):

```bash
pip install -r requirements.txt
python -m runner --max-uncited-pct 5                  # citation gate
python -m orchestrator_runner --max-fail-pct 0        # orchestrator + tool-routing
python -m runner --with-foundry                       # optional, needs AZURE_OPENAI_ENDPOINT
EVAL_MODE=live ORCHESTRATOR_URL=https://... python -m orchestrator_runner   # live
```

Red team (`redteam/`): `python -m runner --max-fail-pct 10`.

Bicep sanity: `az bicep build --file infra/main.bicep --stdout > /dev/null`.

Deploy: `azd auth login && azd up` (CI uses `.github/workflows/deploy.yml` via OIDC).

## Architectural contracts — read before editing

1. **Citations are load-bearing.** Every Log Analyst tool returns a `ToolResponse` (`apps/log_analyst/citations.py`) with `citations: list[Citation]` of type `log | runbook | incident`. `ToolResponse.finalize()` auto-tags `warnings: ["uncited"]` when citations are empty. CI fails if >5% of turns are uncited — do not silently drop citations to make tests pass.
2. **Orchestrator `/api/turn` is the eval/red-team surface.** It must reuse the same voice-provider session + tool-routing path as `/ws/voice` so the citation contract is identical. Response shape: `{text, citations[], tool_calls[], warnings[]}`. The orchestrator gate grades `tool_calls` for routing correctness.
3. **Tool registration is table-driven.** Add a tool by creating `apps/log_analyst/tools/<name>.py` exporting a descriptor + handler, then `register()` in `tools/__init__.py`. Errors raised by handlers are wrapped into `ToolResponse` so `citations`/`warnings` are always present — preserve this.
4. **Voice provider is pluggable.** `VOICE_PROVIDER=foundry_realtime|speech_services` selects implementation; both implement `voice.base.VoiceProvider` / `VoiceSession`. Don't bypass this abstraction in `agent/orchestrator.py`.
5. **Auth is keyless.** All Azure SDK clients use `DefaultAzureCredential` against a single user-assigned managed identity (defined in `infra/modules/roleAssignments.bicep`). Never add API-key auth or secrets to env files; secrets flow through Key Vault.
6. **Cosmos partition keys:** `incidents` → `/incidentId`, `conversations` → `/conversationId`.
7. **Pattern signatures in `detect_pattern`** must stay in sync with `data/generate_mock_data.py` — three named signatures (`cascading_doors_then_dwell`, `interlock_pre_emergency`, `shunt_then_power_trip`); a signature matches when every event type appears ≥1× in the window.

## Conventions

- **Python:** 3.11, ruff (line-length 100, selects `E,F,W,I,B,UP` + log_analyst adds `SIM,RUF`), strict mypy. `from __future__ import annotations` at top of new modules. `asyncio_mode = "auto"` — write `async def test_*` without decorators.
- **Tests are hermetic.** Eval/red-team runners replay `cassettes/<scenario-id>.json`; live mode is opt-in via `EVAL_MODE=live` + a service URL var. When adding a scenario YAML, add a matching cassette.
- **Calibration is sacred.** Thresholds live in `evals/calibration.json` / `calibration.md`. Don't tweak `--max-uncited-pct` etc. to make CI green — follow the recalibration protocol in `calibration.md`.
- **Extensions are exercises, not features.** `docs/extensions/NN_*/` ship failing tests + acceptance criteria. Don't pre-implement them in the skeleton.
- **Mock data only.** Don't reference real MTA systems, employees, schedules, or telemetry. Keep rail lines fictional (L1/L2/L3).

## CI gates (must pass on PR)

| Workflow | What it runs |
|---|---|
| `ci.yml` | ruff + `mypy --strict` + pytest for both Python services; eslint + tsc + vitest for frontend; `az bicep build`. Matrix over `[log_analyst, orchestrator]`. |
| `eval.yml` | `citation-gate` (≤5% uncited), `orchestrator-gate` (0% fail), `foundry-evaluators` (each ≥3.0; only when `AZURE_OPENAI_ENDPOINT` repo var set). Path-filtered to `apps/**`, `evals/**`. |
| `redteam.yml` | Manual + weekly Monday 12:00 UTC. Gate: 0 high/critical, ≤10% overall. |
| `deploy.yml` | `azd provision && azd deploy` on push to `main` via OIDC. |

## Squad framework

This repo uses [Squad](`.squad/`) for multi-agent workflows. If you're picking up an issue labeled `squad:{member}`, read `.squad/team.md` and `.squad/routing.md` first. The `.squad/templates/copilot-instructions.md` has the full agent contract. Use branch names `squad/{issue-number}-{slug}` and reference the issue with `Closes #N` in PRs.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

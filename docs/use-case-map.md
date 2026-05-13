# Use Case Map — MTA AI Hackathon Accelerator

> **For forking teams.** The hackathon's baseline is your Devpost-provisioned Azure + GitHub Copilot sandbox; every team has that. This accelerator is opt-in: a working Hour-1 baseline that forking teams extend toward their use case. If your team is greenfielding instead, treat the rows below as architectural references — patterns to lift, not a path to follow.

Find the row that sounds most like your problem. **Where it lives** points you to what the skeleton already does. **Tailoring recipe** points you to the 30-min swap in [participant-tailoring.md](participant-tailoring.md) or the relevant extension under [extensions/](extensions/).

## How to read this map
- **Your use case** = paraphrased from what MTA teams submitted on the registration form.
- **Archetype** = A (Agentic Ops), B (Legacy Modernization), C (Data Platform). Most use cases blend two.
- **Where it lives** = the specific path that demonstrates the pattern. Start there.
- **Tailoring recipe** = the 30-minute swap guide that turns the example into your scenario.
- **Effort dial** = realistic ambition for a 1.5-day hackathon. Pick the dial that matches your team's skill, not the one that sounds most impressive.

## The map

| # | Your use case (as submitted) | Archetype | Where it lives | Tailoring recipe | Effort dial |
|---|---|---|---|---|---|
| 1 | Intelligent log analyzer + incident pattern recognition for train control systems | A | `apps/log_analyst/` — Log Analyst specialist + its three tools (`search_logs`, `detect_pattern`, `summarize_incident`) | [Recipe 1: Swap the Specialty](participant-tailoring.md#recipe-1) | **Demo-ready as-is.** Replace mock log corpus with your team's synthetic samples → present. |
| 2 | Modernize PA/CIS SCADA distributed system monitoring | A | [Extension 01](extensions/01_add_health_analyst/) — Health Analyst specialist | Recipe 1 | Medium. Swap the mock health-report schema for a SCADA-event schema; add a second tool for event correlation. |
| 3 | Automate sending database health reports to an AI agent to discover hidden problems | A | [Extension 01](extensions/01_add_health_analyst/) `find_hidden_issues` tool + [Extension 08](extensions/08_custom_evals/) | Recipe 1 | Easy. Point the tool at your mock DB-health JSON, tweak the system prompt, run the eval suite. |
| 4 | Modernize PCICS — ASP.NET MVC + on-prem SQL → modern API + UI | B + C | `legacy/` (drop your slice) → modernized to FastAPI in `apps/orchestrator/` style. Extensions [04](extensions/04_legacy_modernization/) + [09](extensions/09_postgres_target/) | [Recipe 2: Swap the Legacy App](participant-tailoring.md#recipe-2) | High but high-value. Drop a slice of your legacy controller into `legacy/`, run the GitHub Copilot modernization walkthrough, deploy the new API to ACA. |
| 5 | .NET Framework 4.8 → .NET 10 migration (template + several legacy codebases) | B | `legacy/` + [Extension 06](extensions/06_enable_modernize_pr/) (Copilot-assisted refactor PR pipeline) | Recipe 2 | Medium. Copy your .csproj into `legacy/`, follow `legacy/README.md`, let Copilot drive the refactor PR. |
| 6 | Train Performance Corporate Data Warehouse — modernize source + ELT | C | `scripts/load_search_index.py` + `data/` ingestion pattern + Bicep for Postgres ([Extension 09](extensions/09_postgres_target/)) | [Recipe 3: Swap the Data Source](participant-tailoring.md#recipe-3) | Medium. Replace mock log loader with your mock ELT job; index the output into AI Search so the agents can query it. |
| 7 | Modernize MTA microservices | B | `apps/log_analyst/` & (after Ext 01) `apps/health_analyst/` — already FastAPI microservices on ACA | Recipe 2 | Easy. Drop one of your services in next to these; the Bicep already provisions for additional ACA apps. |
| 8 | Various on-prem legacy applications (web + desktop) | B | `legacy/` (web sample) + [Extension 04](extensions/04_legacy_modernization/) (pattern; no desktop sample shipped) | Recipe 2 | Medium. Web app path is paved. Desktop app path is "extract the business logic into a Python service, front it with a web UI" — pattern only. |
| 9 | Create a pipeline using GitHub Actions | DevOps spine | `.github/workflows/` — `ci.yml`, `eval.yml`, `deploy.yml`, `modernize-pr.yml.disabled` | None — every fork inherits these | **Free.** You inherit four working workflows. Modify deploy targets and you're done. |
| 10 | App modernization, UI enhancement | B | `apps/frontend/` — React + Vite + shadcn/ui voice UI; [Extension 07](extensions/07_frontend_rebrand/) | Recipe 2 | Easy. Use the existing voice frontend as your modern UI; rebrand and rewire to your modernized API. |
| 11 | Many processes for handling data and reports | C | `scripts/load_search_index.py` + Cosmos `incidents` container | Recipe 3 | Easy. Pick one report type; mock 50 samples; load them; ask the orchestrator to summarize. |
| 12 | "Open to ideas" / "Nothing specific" | All three | Start at the Hour-1 demo and pitch from there | Whichever recipe fits the pitch you pick | Use the demo as-is and present. That alone wins judging. |
| 13 | PowerApp + Dataverse chatbot for non-technical users *(Track 1)* | Bridge | Track 1 territory — hand off to Track 1 coaches | Out of scope for Track 2 | Hand-off. The connector pattern (Foundry agent as a custom connector consumed from Copilot Studio) is documented but the Copilot Studio build happens in Track 1. |
| 14 | Power Pages / Power Apps development *(Track 1)* | Bridge | Track 1 — coach hand-off | Out of scope | Track 1 territory. |

## What the map is telling you

- **The Hour-1 skeleton ships only `apps/log_analyst/`.** Everything else (Health Analyst, legacy slice, modernize-pr workflow, custom evals, Postgres) is reached through numbered extensions. Forking teams complete extensions during the event — that's where their demo content gets built.
- **9 of the 12 dev-track use cases land on 3 reachable paths**: `apps/log_analyst/` (shipped), `apps/health_analyst/` (Extension 01), `legacy/` (Extension 04). Master those three and you can ship every forking team.
- **The GitHub Actions ask (#9) is free** for forkers — you inherit `ci.yml` / `eval.yml` / `deploy.yml`. The DevOps modernization story is part of the floor, not a separate track.
- **Use cases #13 and #14 are Track 1 escapees.** Don't try to solve them here. Hand off.
- **"Open to ideas" cohorts (#12) are your biggest team-formation opportunity.** In the opening session, pitch use cases #1, #2, and #4 — concrete, demoable, and well-served by the accelerator.

## Coach quick-reference

| Stuck on | Point them at | Time to unstick |
|---|---|---|
| "Should we fork or greenfield?" | Fork if team has ≥1 Beginner with Copilot. Otherwise greenfield, use this repo as reference. | 2 min |
| "How do we add our own tool to an agent?" | [Extension 03](extensions/03_add_tool/) | 15 min |
| "How do we ground on our own data?" | [Recipe 3](participant-tailoring.md#recipe-3) / [Extension 02](extensions/02_swap_grounding_corpus/) | 30 min |
| "Voice isn't working in our sub" | [docs/voice.md § Speech Services fallback](voice.md#fallback-azure-speech-services-stt--tts) — flip `VOICE_PROVIDER` | 10 min |
| "How do we modernize this legacy thing?" | [Extension 04](extensions/04_legacy_modernization/) | 45 min |
| "We need a CI/CD pipeline" | `.github/workflows/deploy.yml` — already done if you forked | 0 min |
| "We're greenfielding — can we still copy patterns?" | Yes. Lift anything from `apps/` or `infra/` as reference; no fork required. | 5 min |

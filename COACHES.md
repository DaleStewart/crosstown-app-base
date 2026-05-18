# For Hackathon Coaches

Welcome — this repo is the Track 2 reference stack for the MTA AI Agent Hackathon. It's built to be **forked by teams** and extended toward their submitted use case.

## What you should see in the demo

1. Open the **rider copilot demo:** https://frontend.blackriver-0ab9be19.swedencentral.azurecontainerapps.io/
2. Try: "Tell me about service to Brooklyn today" (text input is most reliable)
3. You should see:
   - The user message on the left
   - A **"Tool calls"** panel showing `get_disruption_status` (or similar) with line + citations
   - An assistant text reply with line-level disruption info
   - Source links in the citations

**Demo win:** tool-call panel visible = proof the orchestrator routed to the right specialist and wired the result back. This scores **Agent Architecture & Foundry Use (30% weight).**

## What to grade

See **[docs/use-case-map.md](docs/use-case-map.md)** — it maps every MTA use case back to:
- Where it lives in the skeleton
- Which extension the team should tackle
- Effort dial for a 1.5-day hackathon

**Key observation:** If a team forks this repo and uses **text input only**, that's a valid choice — voice is a stretch goal, not required.

## Judging app

🔗 https://mango-hill-0ee13cb0f.7.azurestaticapps.net/

- Sign in with **GitHub** (you'll be added as admin)
- See your assigned teams and their scores
- Post scores on the Scoring tab
- Runbook + MTA signage reference on the Runbook tab

**If you see a 500 on /api/teams:** Screenshot the DevTools response body and share it with Sean (@segayle on GitHub) — diagnostic instrumentation is in place to help debug.

## Where the agents live

The orchestrator dispatches to specialists based on the user's intent:

| Specialist | Path | Tools |
|---|---|---|
| **Log Analyst** | `apps/log_analyst/` | `search_logs`, `detect_pattern`, `summarize_incident` |
| **Service Advisor** | `apps/service_advisor/` | `get_disruption_status`, `find_alternate_route`, `get_shuttle_bridging`, `recommend_commute_action` |

Full architecture: [docs/architecture.md](docs/architecture.md)

## Routing & citing

The orchestrator:
1. Receives user input (text or transcribed voice)
2. Routes to the appropriate specialist based on intent
3. Specialist calls one or more **tools**, each with `citations[]` metadata
4. Orchestrator composes a final reply with those citations
5. Frontend displays tool calls + citations in a panel

**This is the core of the score:** tool calling + cited responses = proof the team wired Foundry agents correctly.

## Known posture (Tue 2026-05-19)

- ✅ **Text input:** stable, recommended for demo
- ✅ **Tool calls & citations:** working end-to-end
- ✅ **Voice input:** working end-to-end; assistant reliably replies (brief overlap possible on rapid follow-up)
- ✅ **Foundry Realtime:** stable, PR #60 fixed the voice loop cycle-2 empty-response issue

## Common coaching moments

| Team says | You say |
|---|---|
| "Should we fork or greenfield?" | Fork if ≥1 team member knows Copilot. Otherwise greenfield, use this repo as reference. See [docs/use-case-map.md](docs/use-case-map.md). |
| "How do we add our own tool?" | [Extension 03](docs/extensions/03_add_tool/) — 30 min. Pattern: define tool signature → add to specialist → register in routing. |
| "How do we swap the data?" | [Extension 02](docs/extensions/02_swap_grounding_corpus/) — 30 min. Drop your corpus in `data/`, run the indexer. |
| "Voice isn't working" | Set `VOICE_PROVIDER=speech_services` in `.env`. Azure Speech Services is the fallback. See [docs/voice.md](docs/voice.md). |
| "We need a modernization example" | [Extension 04](docs/extensions/04_legacy_modernization/) — 60 min. Swap a .NET legacy slice into `legacy/`, let Copilot refactor it. |

## For teams new to Foundry agents

The skeleton ships:
- **One working specialist** (Log Analyst) that demonstrates tool calling + citations
- **One extended specialist** (Service Advisor) for disruption handling
- **All the plumbing** (orchestrator, Foundry relay, eval gates) ready to go

Teams fork, add a **third specialist** or swap the grounding data, and that's a complete demo for judges.

## Resources

- **Architecture & data flow:** [docs/architecture.md](docs/architecture.md)
- **Voice details:** [docs/voice.md](docs/voice.md)
- **Use case → extension map:** [docs/use-case-map.md](docs/use-case-map.md)
- **Tailoring recipes (3 × 30 min swaps):** [docs/participant-tailoring.md](docs/participant-tailoring.md)
- **Extensions 01–09:** [docs/extensions/](docs/extensions/)
- **Evals & red team:** [docs/evals.md](docs/evals.md), [docs/redteam.md](docs/redteam.md)

## Questions?

- **Stuck on tooling?** → DM Sean (@segayle on GitHub)
- **Stuck on architecture?** → See [docs/architecture.md](docs/architecture.md) or flag another Track 2 coach
- **Track 1 question (Power Apps)?** → Hand off to a Track 1 coach

Good luck! 🚇

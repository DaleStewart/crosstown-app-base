# Squad Decisions

## Active Decisions

### Post-Demo Roadmap: Next Feature Selection (2026-04-21)
**Timestamp:** 2026-04-21T17:55:00Z  
**Authority:** User (msftsean via Morpheus)  
**Decision:** Conversation Persistence & History (Cosmos DB session storage) selected as next candidate feature for speckit.plan.

**Rationale:**
- Closes demo → production gap with minimal risk (additive infrastructure, no voice/phone changes)
- Unlocks ServiceNow integration as natural follow-on (tickets require persistent sessions)
- Supports "Reuse Across Campus" narrative (persistence = institutional memory, prerequisite for trust)
- Medium complexity, high teaching value (Lab 08 candidate: "Production Persistence")

**Deferred candidates with rationale:**
- **ServiceNow Integration (#2):** High value but requires instance access, credentials, departmental coordination
- **Human Handoff & Coach Dashboard (#3):** Large scope; best after persistence + ticketing land
- **Multi-Tenant (#4):** Architectural change; premature before second institution adopts
- **Analytics & Observability (#5):** Non-blocking; high value but can be added incrementally

**Reference:** See `specs/roadmap/next-feature-recommendation-2026-04-21.md` for full feature analysis and speckit.plan kickoff prompt.

### Model Selection Directive
**Timestamp:** 2026-03-13T13-09-59  
**Authority:** User (msftsean via Copilot)  
**Decision:** 
- Code-writing agents (Tank, Switch, Mouse, Neo): use `claude-sonnet-4.6`
- Non-code agents (Scribe, documentation, evals, Morpheus when not reviewing): use `claude-haiku-4.6`

**Rationale:** Optimize for cost vs. quality based on task type. Code work requires full Sonnet capability; administrative/documentation work can use faster Haiku model.

### Azure Resources Ready for Live Testing
**Timestamp:** 2026-03-13T17:34  
**Authority:** User (msftsean via Copilot)  
**Decision:** Azure resources provisioned and ready for live voice testing.
- **Resource Group:** `rg-47doors-voice` (eastus2)
- **Resource Name:** `oai-47doors-voice`
- **Deployments:** `gpt-4o` + `gpt-4o-realtime`

**Rationale:** User directive to plan for live Azure testing, not just mock mode. Infrastructure is in place and ready for Phase 3+ endpoint validation.

## Archive

See \decisions-archive.md\ for decisions dated 2026-03-13 through 2026-04-20.

# Tank (Backend Dev) — Work History

## Recent Work

### KB Search Query Fix (2026-04-09T0620)
- **Fixed:** `ActionAgent._search_knowledge_with_content()` building queries from intent labels instead of user messages
- **Impact:** Financial aid query now returns "Financial Aid Disbursement Schedule" (score 1.0) instead of irrelevant articles
- **Commit:** 824ae01 — fix(search): use original message for KB search queries
- **Tests:** All 461 pass, deployed to Azure Container Apps

### Pipeline Fix (2026-04-09T0500)
- **Fixed:** QueryAgent prompt schema mismatch, conversation serialization bug, nginx REST/WS routing
- **Result:** All 461 tests pass, deployed backend + frontend
- **Commit:** 4d66431
- **Impact:** KB search returns articles, human escalation creates tickets, all 4 services UP

### Post-Demo Roadmap Analysis (2026-04-21)
- **Roadmap recommendation:** Next feature is Conversation Persistence & History (Cosmos DB session storage)
- **Builds on:** Existing session_id model used across text, browser voice, and phone transcripts
- **Impact:** Enables multi-visit support journeys, unlocks ServiceNow integration, supports "Reuse Across Campus" narrative
- **See:** `specs/roadmap/next-feature-recommendation-2026-04-21.md` and `.squad/decisions.md`

## Ongoing
KB search pipeline stable. Persistence feature (Cosmos DB sessions) prioritized for next build cycle. Ready to review roadmap and kick off speckit.plan for 003-conversation-persistence.

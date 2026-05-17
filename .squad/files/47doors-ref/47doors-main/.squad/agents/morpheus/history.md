# Project Context

- **Owner:** msftsean
- **Project:** 47 Doors — Universal Front Door Support Agent for university student support
- **Stack:** Python 3.11+ / FastAPI 0.109+, TypeScript 5 / React 18, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- **Architecture:** Three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with voice interaction via Azure OpenAI GPT-4o Realtime API / WebRTC
- **Created:** 2026-03-13

## Learnings

- **Doc Fleet Pattern**: Major features ship across four parallel doc surfaces: (1) technical specs in `specs/` (Tank's domain), (2) runbook/workshop site (Switch's domain), (3) participant & coach guides (narrative, Morpheus), (4) release notes + changelog (both coordinated). When a feature ships to production, all four surfaces must be updated for coherent narrative flow and participant understanding.

- **App State (2026-04-21)**: Production system is a three-agent pipeline (QueryAgent → RouterAgent → ActionAgent) with full voice capabilities (browser WebRTC + phone bridge via ACS). 435+ backend tests passing, 8-hour boot camp curriculum complete. Current boundaries: single-tenant, in-memory sessions (no persistence), mock ServiceNow tickets, no human handoff dashboard. Workshop runbook emphasizes "Reuse Across Campus" and "Trust Boundaries" as forward themes.

- **Next Feature Candidates (2026-04-21)**: Analyzed 5 candidates post-voice-production. Top recommendation: **Conversation Persistence & History** (Cosmos DB). Medium complexity, high value — closes demo→production gap, unlocks ServiceNow integration, supports multi-visit student journeys, perfect Lab 08 material. Deferred: ServiceNow (needs persistence first), Human Handoff (large scope), Multi-Tenant (premature), Analytics (non-blocking). See `specs/roadmap/next-feature-recommendation-2026-04-21.md`.

## Work Log

### 2026-04-21T23:00:00Z — Post-Production Roadmap Analysis & 002 Spec Closeout (Morpheus)
Analyzed production state after successful phone bridge demo and recommended next feature for speckit.plan.

**Part 1: Closed out specs/002-voice-interaction/ as shipped**
- Updated spec.md, plan.md, tasks.md with production status (revision `azd-1776792457`, 2026-04-21)
- Marked Phases 1-3 + Phase 7 complete, Phases 4/5/6/8 deferred (existing pipeline covers core needs)
- Updated DEMO_RUNBOOK.md, FEATURE_SUMMARY.md, checklists/requirements.md with shipped status
- Added cross-links to CHANGELOG, RELEASE_NOTES, Azure Realtime API Schema skill

**Part 2: Comprehensive roadmap analysis**
- Surveyed app state: 3-agent pipeline, browser+phone voice, 435+ tests, 8-hour boot camp, workshop runbook
- Inventoried existing specs (002 shipped, 001 never existed — organic build)
- Identified 5 candidate features: (1) Conversation Persistence, (2) ServiceNow Integration, (3) Human Handoff Dashboard, (4) Multi-Tenant, (5) Analytics
- **Recommended: Conversation Persistence & History** — Medium complexity, closes demo→production gap, unlocks ServiceNow sync, supports "Reuse Across Campus" narrative, perfect Lab 08 candidate
- Created `specs/roadmap/next-feature-recommendation-2026-04-21.md` with full analysis, rationale, speckit.plan kickoff prompt

**Commit:** `5a084cd`

**Artifacts created:**
- `specs/roadmap/next-feature-recommendation-2026-04-21.md` — full recommendation document
- `.squad/decisions/inbox/morpheus-next-feature-recommendation.md` — decision inbox entry

**Rationale:** Voice is production-verified; persistence is the natural next step to enable multi-visit support journeys and unlock real ticketing integration. ServiceNow can't sync status updates to sessions that disappear when the browser closes.

### 2026-04-21T22:30:00Z — Phone Bridge Live: Narrative Doc Sweep (Morpheus)
Updated participant-facing and coach docs to reflect production-verified phone integration.

**Changes:**
- `docs/RELEASE_NOTES.md` — Added Version 0.1.5 entry noting phone bridge live, bidirectional transcripts, production architecture
- `docs/bootcamp/PARTICIPANT_GUIDE.md` — Updated "What You're Building" to reflect phone calls fully working (not just "coach demo"); updated bonus assessment criteria
- `docs/bootcamp/QUICK_REFERENCE.md` — Clarified live phone number (+1-913-217-1946), corrected Phone env vars table (required vs. default), emphasized production verification
- `coach-guide/FACILITATION.md` — Inverted voice/phone demo section to assert "phone demo is live"
- `coach-guide/TALKING_POINTS.md` — Added production-verified backend stack to voice/phone transition talking point
- `coach-guide/TROUBLESHOOTING.md` — Replaced phone troubleshooting entries with verification steps and expected signals on `/live`

**Commit:** `599cc8e`

**Cross-team coordination:** Tank updated backend code & CHANGELOG; Switch updating runbook site. This update completes the narrative surface (participant guides, coach guides, release notes).

### 2026-03-13T18:46:00Z — Azure-First Spec Update (Morpheus)
Updated `specs/002-voice-interaction/spec.md` to prioritize Azure Container Apps as primary deployment target.

**Changes:**
- MVP scope: Added "Azure Container Apps deployment"
- VFR-026–029: Deployment requirements (Azure primary, local dev secondary, parity)
- Updated assumptions and dependencies to reflect Azure-first strategy
- Mock mode clarified as dev/test tool, not demo default

**Commit:** `71a91d6`

**Cross-agent impact:** Tank's Phase 1 deployment config must align with these requirements.

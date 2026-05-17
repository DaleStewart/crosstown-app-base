# Next Feature Recommendation: Post-Voice Production Roadmap

**Date**: 2026-04-21  
**Requested by**: msftsean (Sean)  
**Prepared by**: Morpheus (Lead)  
**Context**: Post-production deployment review after successful phone bridge demo (revision `azd-1776792457`)

---

## Current State Snapshot

As of 2026-04-21, **47 Doors** is a production-ready three-agent AI support system (QueryAgent → RouterAgent → ActionAgent) deployed on Azure Container Apps with full voice interaction capabilities. The system provides:

**Core Capabilities (Shipped)**:
- Text chat interface with intent detection, routing, ticket creation, and knowledge retrieval
- Real-time voice interaction via Azure OpenAI GPT-4o Realtime API over WebRTC (browser)
- Phone bridge via Azure Communication Services (+1-913-217-1946) connecting PSTN callers to the same voice pipeline
- Live transcript dashboard at `/live` showing bidirectional caller+agent conversation in real time
- Mock mode for development and demos without Azure credentials
- Graceful degradation to text-only when voice is unavailable
- PII filtering across all modalities (text, browser voice, phone)
- 4-tool agent pipeline exposed to voice: `analyze_and_route_query`, `check_ticket_status`, `search_knowledge_base`, `escalate_to_human`

**Educational Footprint**:
- 8-hour boot camp curriculum with 8 progressive labs (00-setup through 07-mcp-server)
- Complete coach guide (facilitation, talking points, troubleshooting, assessment rubric)
- Participant guide and quick reference documentation
- Workshop runbook site with 12 presentation tabs covering architecture, demo walkthrough, responsible AI, trust boundaries, voice accessibility, telephony, and "Reuse Across Campus"

**Infrastructure**:
- Backend: Python 3.11+, FastAPI 0.109+, Azure OpenAI, Azure AI Search, Pydantic v2.5+
- Frontend: TypeScript 5, React 18, WebRTC for browser voice
- Phone: Azure Communication Services Call Automation bridged to Realtime API
- Deployment: Azure Container Apps via `azd up`, managed identity auth, ephemeral tokens
- Testing: 435+ backend tests passing (338 unit/mock + 97 GPT-4o evals), frontend unit tests green

**Known Boundaries**:
- Single-tenant demo/EDU deployment (no multi-tenancy)
- In-memory session store (no persistence layer)
- Simulated ServiceNow ticket creation (no actual ticketing system integration)
- 54 knowledge base articles (Financial Aid, Registration, Housing, IT Support, Policies)
- No authentication on main chat app (workshop site has Azure AD via SWA)
- Voice sessions limited to 10 minutes (configurable)

---

## Existing Specs Inventory

| Folder | Status | Summary |
|--------|--------|---------|
| `specs/002-voice-interaction/` | ✅ **Shipped** (2026-04-21, rev `azd-1776792457`) | Real-time voice via WebRTC + phone bridge via ACS. Phases 1-3 + Phase 7 complete. Phases 4 (escalation enhancements), 5 (hybrid UI polish), 6 (accessibility audit), 8 (security hardening) deferred. Browser voice + phone parity achieved. |
| `specs/001-boot-camp-labs/` | ❌ **Does not exist** | Boot camp labs were built organically without a formal spec (curriculum exists in `labs/` + `docs/bootcamp/` + `coach-guide/`). No retroactive spec needed. |

**Note**: Only one formal spec exists. The project started with boot camp labs built directly, then voice was spec-driven. This indicates the team is comfortable with both organic and spec-driven workflows.

---

## Candidate Features

| Name | What | Why Now | Complexity | Dependencies |
|------|------|---------|-----------|--------------|
| **1. Conversation Persistence & History** | Add persistent session storage (Cosmos DB or Azure Table Storage) so students can resume conversations across browser sessions, view conversation history, and retrieve past ticket IDs. Include admin dashboard to view session analytics. | **High value post-demo**: Persistence unlocks multi-visit support journeys. Demo showed "one call" magic; production needs "returning student" continuity. Workshop runbook mentions "Reuse Across Campus" — this enables institutional memory. Closes gap between demo polish and real-world use. | **M** (Medium) | Azure Cosmos DB or Table Storage provisioning in Bicep; session schema migration; frontend session list UI; backend session CRUD endpoints. No voice/phone changes needed (sessions already have UUIDs). |
| **2. ServiceNow Integration (Real Ticketing)** | Replace simulated ticket creation with actual ServiceNow REST API calls. Map agent-detected departments to ServiceNow assignment groups. Sync ticket status bidirectionally so `check_ticket_status` returns live data. | **Production-critical gap**: Mock tickets work for demos but break trust in real deployment. EDU IT departments already run ServiceNow — this is the bridge to existing workflows. High ROI for "reuse across campus" narrative (workshop runbook Tab 7). | **M-L** (Medium-Large) | ServiceNow instance + credentials; ServiceNow REST API client; mapping config for departments → assignment groups; error handling for API downtime. Voice/phone already call `ActionAgent.create_ticket()`, so no modality changes needed. |
| **3. Human Handoff & Coach Dashboard** | Build a live coach dashboard showing escalated tickets awaiting human review. Coaches claim tickets, send replies (text or voice note), and close loops. Optionally enable real-time voice handoff (transfer caller to live human). | **Demo → Production maturity**: Runbook emphasizes "trust boundaries" and "responsible AI" — human-in-the-loop is the proof point. Phone demo showed AI works; now show AI knows when to step aside. Strengthens EDU credibility (FERPA, sensitive topics require human judgment). | **L** (Large) | WebSocket or SSE for real-time dashboard updates; coach authentication (extend Azure AD from workshop site); ticket claim/assignment logic; voice transfer requires ACS call transfer API. Large scope but high narrative payoff. |
| **4. Multi-Tenant Campus Deployment** | Add tenant isolation so multiple universities (or multiple colleges within one university) can share the same deployment with isolated knowledge bases, department routing, and branding. Tenant detected via subdomain (`college-a.47doors.edu`) or API key. | **"Reuse Across Campus" unlock**: Workshop runbook explicitly calls out scaling to multiple departments/campuses. Single-tenant demo is compelling; multi-tenant deployment is compelling *at scale*. Positions 47 Doors as platform, not one-off. | **L** (Large) | Tenant data model + middleware; tenant-scoped KB indexing in AI Search; per-tenant routing rules; subdomain routing or API key middleware; UI branding config. Large architectural change — best after persistence/ticketing land. |
| **5. Analytics & Observability Dashboard** | Add Application Insights instrumentation for intent accuracy, escalation rate, voice session duration, ticket resolution funnel. Build admin dashboard showing: top intents, PII detection rate, department load, voice vs. text usage, phone call volume. | **Post-demo reflection**: Now that the system works, *measure* how well it works. Supports "65% first-contact resolution" claim in README with real data. Workshop coaches want this for boot camp assessment (did the agent improve over 8 hours?). Enables A/B testing of prompt changes. | **S-M** (Small-Medium) | App Insights SDK wiring (telemetry emit from agents); KQL queries for metrics; frontend dashboard with chart.js or similar; storage for historical trends (optional). Low risk, high teaching value (observability is missing from boot camp labs). |

---

## Recommendation

**Build next: Conversation Persistence & History (Candidate #1)**

### Rationale

The phone demo landed perfectly — callers speak, transcripts render live, the 3-agent pipeline handles real queries. But the demo narrative is "single-call magic": student calls once, gets answer, hangs up. Real student support is a *journey* across days or weeks: "I called about financial aid yesterday, what was my ticket number?" or "Show me my conversation history." Without persistence, every session is ephemeral — students can't return, coaches can't audit, and the "universal front door" metaphor breaks down (doors with no memory aren't trusted entry points).

**Why this feature, why now:**

1. **Closes the demo → production gap with minimal risk**: Persistence is pure additive infrastructure (Cosmos DB + backend CRUD). No changes to voice/phone logic, no new modalities, no risky integrations. The hardest parts (voice, phone, agents) already work. This makes them *useful* beyond the demo.

2. **Unlocks ServiceNow integration (Candidate #2) as a natural follow-on**: Real ticketing systems expect sessions to persist. You can't sync ticket status updates if the session disappears when the browser closes. Persistence first, then ticketing — sequential value delivery.

3. **Supports "Reuse Across Campus" narrative from workshop runbook**: Tab 7 (ReuseAcrossCampus.tsx) talks about scaling to multiple departments. A department can't reuse a system that forgets conversations the moment the student leaves. Persistence is the prerequisite for cross-department trust.

4. **Medium complexity with high teaching value**: Adding Cosmos DB, CRUD endpoints, and a session history UI is a perfect Lab 08 candidate — "Stateful AI Systems" or "Production-Ready Persistence." Boot camp currently ends at deployment (Lab 06); this extends the learning path into post-deployment concerns.

**What gets deferred and why:**

- **ServiceNow Integration (#2)**: Absolutely critical for real deployment, but requires access to a ServiceNow instance, API credentials, and departmental buy-in on assignment group mappings. Higher external coordination cost. Do persistence first, then tackle this with real data to test against.
  
- **Human Handoff (#3)**: Large scope (coach dashboard + real-time updates + optional voice transfer). Also requires rethinking the escalation UX beyond "create escalation ticket." Best done *after* persistence + ticketing land, so coaches see real ticket history when they claim an escalation.

- **Multi-Tenant (#4)**: Architecturally significant change (tenant middleware, scoped indexes, per-tenant config). Premature until a second university/college actually wants to use 47 Doors. Build for one tenant well before building for N tenants.

- **Analytics (#5)**: High value but non-blocking. Can be added incrementally alongside any other feature (instrument as you go). Not urgent because the system already works — analytics measure *how well*, but don't unlock new capabilities.

---

## Suggested speckit.plan Kickoff Prompt

```
Plan a feature to add conversation persistence and history to the 47 Doors support agent. Students should be able to resume conversations across browser sessions, view their past conversation history (text + voice transcripts), and retrieve ticket IDs from previous sessions. Admins should have a dashboard showing active sessions, session duration metrics, and conversation counts per department. Use Azure Cosmos DB for storage (align with existing Azure-first stack). The existing in-memory session store should remain as a fallback for local development. Build on the session model established in 002-voice-interaction (session_id UUID is already the join key for text, browser voice, and phone transcripts). Target: enable multi-visit support journeys and unlock future ServiceNow ticket status sync.
```

---

## Out-of-Scope / Deferred Items

| Feature | Reason for Deferral |
|---------|---------------------|
| **Advanced voice features (emotion detection, voice biometrics, multi-language)** | Spec 002 Phase 4/6/8 items — polish over new capability. Current voice quality is production-grade; these are enhancements, not gaps. |
| **Real-time co-browsing or screen sharing** | Not mentioned in constitution, runbook, or specs. Interesting but no clear demand signal. Students can share screenshots via text chat if needed. |
| **Integration with Canvas LMS / student portal SSO** | High value for production but requires institutional partnerships and SSO setup. Better as a customization per deployment, not core 47 Doors spec. |
| **Voice call recording and playback** | Constitution Principle III explicitly avoids storing raw audio ("PII-filtered transcripts only"). Recording would violate design principle. |
| **Chatbot builder / low-code agent designer** | Interesting for "reuse across campus" but scope creep — 47 Doors is a reference implementation, not a platform builder. Keep it focused. |

---

## Suggested Next Steps

1. **Review this recommendation** with Sean and squad (confirm priority alignment).
2. **Run `/speckit.plan`** with the kickoff prompt above to generate `specs/003-conversation-persistence/` artifacts (spec.md, plan.md, data-model.md).
3. **Provision Cosmos DB** in `infra/main.bicep` (or Azure Table Storage if cost is a concern for EDU demos — Cosmos has free tier).
4. **Implement in phases**:
   - Phase 1: Cosmos session CRUD (replace in-memory store)
   - Phase 2: Session list API + frontend "My Conversations" page
   - Phase 3: Admin dashboard with session metrics
   - Phase 4: Retention policy (auto-delete sessions >90 days, configurable)
5. **Update boot camp labs** — add Lab 08: "Production Persistence" showing Cosmos integration and CRUD patterns.
6. **After 003 ships**, kick off **ServiceNow Integration (Candidate #2)** to close the ticketing loop.

---

**End of Recommendation**  
*For questions or clarifications, see `.squad/decisions/inbox/morpheus-next-feature-recommendation.md` or reach out to Morpheus.*

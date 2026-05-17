# Feature Specification: Universal Front Door Support Agent

**Feature Branch**: `1-front-door-agent`
**Created**: 2026-01-20
**Last Updated**: 2026-02-26
**Status**: Draft
**Input**: User description: "Universal Front Door Support Agent - Three-agent system for routing student support requests to correct departments, creating tickets, retrieving knowledge, and escalating complex issues to humans"

## Problem Statement

Universities suffer from a "47 front doors" problem where students must navigate multiple disconnected support channels. Students are transferred 3+ times on average, must re-explain their problem at each handoff, don't know which department handles their issue, wait times exceed 20 minutes, and after-hours requests go unanswered. Current first-contact resolution rate is only 40%.

## Networking & Proxy Requirements (Codespaces / Dev Containers)

The frontend and backend communicate through a Vite dev server proxy. These requirements **must** be followed to avoid connectivity failures in GitHub Codespaces and similar remote environments:

### Rule 1: `VITE_API_BASE_URL` must be empty in Codespaces

The `frontend/.env` file must have `VITE_API_BASE_URL=` (empty). Setting it to `http://localhost:8000` causes the **browser** (running outside the container) to call `localhost:8000` directly, which is unreachable. With an empty value, API calls use relative paths (`/api/...`) and are proxied by the Vite dev server to the backend inside the container.

### Rule 2: Vite proxy must target `127.0.0.1`, not `localhost`

In `frontend/vite.config.ts`, the proxy target must be `http://127.0.0.1:8000` (explicit IPv4). Using `http://localhost:8000` can fail because:

- Vite (Node.js) may resolve `localhost` to IPv6 `::1`
- Uvicorn binds to IPv4 `0.0.0.0` by default
- The IPv4/IPv6 mismatch causes silent 500 errors with empty response bodies

### Rule 3: Uvicorn must bind to `0.0.0.0`

The backend must start with `--host 0.0.0.0` so it accepts connections from the Vite proxy and Codespaces port forwarding. This is already configured in the startup command.

## Azure Deployment Reliability Requirements

These requirements are based on validated deployment behavior in GitHub Codespaces and constrained enterprise subscriptions.

1. Interactive browser login MAY be blocked by Conditional Access (`AADSTS53003`) for Azure CLI/azd. The deployment workflow MUST support non-interactive service principal authentication.
2. Infrastructure templates MUST allow Cosmos DB region decoupling from app-hosting region to handle regional capacity constraints.
3. Deployment documentation MUST include provider registration prerequisites (`Microsoft.App`, `Microsoft.Web`) and a fallback path when registration requires subscription-level admin rights.

## Vision

Create a single, intelligent entry point that receives any student support request, detects intent, routes to the correct department, creates tickets in appropriate systems, retrieves relevant knowledge, and escalates complex or policy-related issues to humans—eliminating the "47 front doors" problem and increasing first-contact resolution from 40% to 65%.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Submit Standard Support Request (Priority: P1)

A student has a common support issue (password reset, transcript request, facilities report) and needs quick resolution without knowing which department to contact.

**Why this priority**: This represents 80%+ of all support requests. Solving standard routing correctly delivers immediate value to most students and validates the core intent detection and routing logic.

**Independent Test**: Can be fully tested by submitting a standard query like "I forgot my password" and verifying the system returns a ticket ID, correct department routing, and relevant knowledge articles within 30 seconds.

**Acceptance Scenarios**:

1. **Given** a student is logged in, **When** they submit "I forgot my password", **Then** the system creates a ticket routed to IT, returns a ticket ID, and displays relevant password reset articles.
2. **Given** a student submits "The elevator in Smith Hall is broken", **When** processed, **Then** the system extracts "Smith Hall" as a building entity and routes to Facilities with appropriate priority.
3. **Given** a student submits "I need a transcript for grad school", **When** processed, **Then** the system routes to Registrar and provides knowledge articles about transcript requests.
4. **Given** a student submits a request after business hours, **When** processed, **Then** the system still creates a ticket, provides knowledge articles, and sets appropriate SLA expectations.
5. **Given** a student submits a common query with a high-relevance knowledge base match (relevance >= 0.5) and low/medium priority, **When** processed, **Then** the system MAY return knowledge articles without creating a ticket (self-service resolution via KB).

---

### User Story 2 - Receive Escalation for Policy-Related Requests (Priority: P2)

A student has a request that requires human judgment (appeals, waivers, exceptions, refunds) and needs their issue properly documented and routed to a human reviewer.

**Why this priority**: Policy decisions cannot be automated and require human judgment. Proper escalation prevents the agent from making unauthorized decisions while ensuring students' requests are properly captured.

**Independent Test**: Can be tested by submitting "I want to appeal my grade" and verifying the system flags for human escalation, creates an escalation ticket, and clearly communicates that human review is required.

**Acceptance Scenarios**:

1. **Given** a student submits "Can I get a refund for this semester?", **When** the system detects "refund" as a policy keyword, **Then** it escalates to human review and informs the student a human will respond.
2. **Given** a student submits "I want to appeal my grade", **When** processed, **Then** the system creates an escalation ticket and provides expected response time for human review.
3. **Given** a student mentions Title IX, mental health crisis, or threat assessment keywords, **When** detected, **Then** the system immediately escalates to appropriate human handlers with urgent priority.

---

### User Story 3 - Track Existing Request Status (Priority: P3)

A student has previously submitted a request and wants to check its status without calling or re-explaining their issue.

**Why this priority**: Status tracking improves student satisfaction and reduces repeat contacts to support staff. Requires session history to function properly.

**Independent Test**: Can be tested by submitting a query, receiving a ticket ID, then asking "What's the status of my ticket?" and receiving accurate status information.

**Acceptance Scenarios**:

1. **Given** a student previously received ticket TKT-IT-123, **When** they ask "What's the status of my ticket?", **Then** the system retrieves the current status from the ticketing system.
2. **Given** a student has multiple open tickets, **When** they ask about status, **Then** the system lists all their recent tickets with status.
3. **Given** a student navigates to the My Tickets view, **When** the view loads, **Then** the system displays all their tickets with current status, department, priority, and timestamps in a master/detail layout.

---

### User Story 4 - Clarify Ambiguous Requests (Priority: P4)

A student submits a vague request that could apply to multiple departments and needs the system to ask for clarification rather than misrouting.

**Why this priority**: Handling ambiguity correctly prevents misrouting and frustration. A follow-up clarification is better than wrong routing.

**Independent Test**: Can be tested by submitting "I need help with my account" and verifying the system asks a clarifying question rather than guessing incorrectly.

**Acceptance Scenarios**:

1. **Given** a student submits "I need help with my account", **When** the confidence score is below 0.70, **Then** the system asks a clarifying question (e.g., "Are you referring to your university login account, your financial account, or something else?").
2. **Given** a student provides clarification after being asked, **When** the clarified intent is processed, **Then** the system routes to the correct department with the full conversation context preserved.
3. **Given** the system cannot resolve ambiguity after 3 clarification attempts, **When** this threshold is reached, **Then** it escalates to human triage.

---

### User Story 5 - Request Human Assistance (Priority: P5)

A student explicitly wants to speak with a human rather than interact with the automated system.

**Why this priority**: Respecting user preference for human contact is essential for trust. Some issues genuinely require human empathy or complex explanation.

**Independent Test**: Can be tested by saying "I need to talk to a person" and verifying immediate escalation to human queue.

**Acceptance Scenarios**:

1. **Given** a student says "I need to talk to a person", **When** processed, **Then** the system immediately routes to human queue without further automated interaction.
2. **Given** escalation to human is triggered, **When** completed, **Then** the system provides estimated wait time and confirms a human will respond.

---

### User Story 6 - Administer Support System (Priority: P6)

An administrator needs to manage incoming tickets, update their status, and configure the system's branding to match their institution.

**Why this priority**: Administrative capabilities are essential for operational management but are secondary to student-facing features.

**Independent Test**: Can be tested by navigating to the Admin view, filtering tickets, updating a ticket status, and modifying branding settings.

**Acceptance Scenarios**:

1. **Given** an administrator opens the Admin dashboard, **When** the view loads, **Then** the system displays all tickets with filtering by status and department.
2. **Given** an administrator selects a ticket, **When** they update its status, assignee, or resolution, **Then** the changes are persisted and reflected immediately.
3. **Given** an administrator navigates to the Branding settings tab, **When** they update the logo URL, primary color, institution name, or tagline, **Then** the changes are applied dynamically across the entire application with a live preview.
4. **Given** an administrator deletes a ticket, **When** confirmed, **Then** the ticket is removed from the system.

---

### Edge Cases

- What happens when a query contains PII (social security numbers, financial data)?
  - System flags PII for secure handling and does not log the raw query content
- How does the system handle queries that span multiple departments (e.g., "My financial aid affects my enrollment")?
  - System detects multi-department coordination need and escalates to human triage
- What happens when sentiment analysis detects high frustration?
  - System increases priority and may proactively offer human escalation
- How does the system handle non-English queries?
  - v1 supports English only; non-English queries receive a message directing to multilingual support line
- What happens if external systems (ticketing, knowledge base) are unavailable?
  - System gracefully degrades: provides best available information and logs for retry, informs user of limited functionality
- What happens if SSO authentication is unavailable?
  - System allows read-only knowledge base browsing; ticket creation and personalized features are blocked until authentication is restored
- What happens when the knowledge base has a highly relevant answer for a low-priority query?
  - System returns KB articles without creating a ticket (KB self-service mode), avoiding unnecessary ticket volume

## Requirements _(mandatory)_

### Functional Requirements

**Intent Detection & Entity Extraction**

- **FR-001**: System MUST analyze natural language queries and detect intent from 28+ categories including: password_reset, login_issues, account_locked, transcript_request, grade_inquiry, enrollment_verification, financial_aid_inquiry, tuition_payment, refund_request, facilities_issue, maintenance_request, room_booking, course_enrollment, add_drop, registration_hold, parking_permit, id_card, housing, grade_appeal, withdrawal_request, waiver_request, work_study, general_question, department_contact, ticket_status, request_followup, request_human, speak_to_person (using LLM-based classification with few-shot prompting)
- **FR-002**: System MUST extract entities from queries including: building names, course codes (pattern: 2-4 uppercase letters + 3-4 digits), dates, urgency indicators, and system names (Canvas, Blackboard, Banner, Workday, Outlook, VPN)
- **FR-003**: System MUST calculate a confidence score (0.0-1.0) for each intent detection
- **FR-004**: System MUST detect PII in queries (SSN, email, phone, credit card, date of birth) and flag for secure handling (not logged in plain text)
- **FR-005**: System MUST analyze sentiment to detect frustrated or urgent tones (classifying as NEUTRAL, FRUSTRATED, URGENT, or SATISFIED)

**Routing & Decision Making**

- **FR-006**: System MUST route queries to one of these departments: IT, HR, Registrar, Financial Aid, Facilities, Student Affairs, Campus Safety, or ESCALATE_TO_HUMAN
- **FR-007**: System MUST escalate to human when confidence score is below 0.70 and clarification attempts have been exhausted (max 3)
- **FR-008**: System MUST escalate to human when policy keywords are detected: appeal, waiver, exception, override, refund, withdrawal deadline
- **FR-009**: System MUST escalate to human for sensitive topics: Title IX, mental health crisis, threat assessment, discrimination
- **FR-010**: System MUST escalate to human when multi-department coordination is needed
- **FR-011**: System MUST escalate to human when user explicitly requests human contact (supporting 13+ trigger phrases including "talk to a person", "speak to someone", "human agent", etc.)
- **FR-012**: System MUST escalate to human after 3 failed clarification attempts
- **FR-013**: System MUST assign priority levels (LOW, MEDIUM, HIGH, URGENT) based on escalation status, sentiment, urgency indicators, and confidence
- **FR-014**: System MUST set SLA expectations based on priority: URGENT=1 hour, HIGH=4 hours, MEDIUM=24 hours, LOW=72 hours

**Ticket Creation & Knowledge Retrieval**

- **FR-015**: System MUST create tickets in the university ticketing system with: ticket ID (format: TKT-{DEPT}-{YYYYMMDD}-{SEQ}, validated by pattern `^TKT-[A-Z]{2,3}-\d{8}-\d{4}$`), department, priority, description, student context
- **FR-016**: System MUST retrieve top 3 relevant knowledge base articles for each query
- **FR-016a**: System MAY skip ticket creation for LOW/MEDIUM priority queries when a knowledge base article with relevance score >= 0.5 provides self-service resolution (KB-only mode)
- **FR-017**: System MUST display knowledge articles with title, URL, and relevance indicator

**Session & Audit**

- **FR-018**: System MUST maintain session context across multi-turn conversations (stateful), with a maximum of 50 conversation turns per session
- **FR-019**: System MUST store session history including: student_id (SHA-256 hashed, 64-character), conversation intents, ticket IDs created
- **FR-020**: System MUST log audit trail: user_id (hashed), query timestamp, detected intent, confidence score, routed department, ticket_id, PII flag, escalation status, escalation reason (required when escalated), sentiment, response time (ms)
- **FR-021**: System MUST NOT log raw query text containing PII beyond audit requirements; PII-containing messages MUST be excluded from ticket descriptions

**Boundaries (What System Must NOT Do)**

- **FR-022**: System MUST NOT approve refunds, waivers, or policy exceptions
- **FR-023**: System MUST NOT modify student records (grades, enrollment, financial data)
- **FR-024**: System MUST NOT access FERPA-protected data beyond routing context
- **FR-025**: System MUST NOT bypass human review for policy-related queries
- **FR-026**: System MUST NOT make enrollment or financial decisions

**User Interface**

- **FR-027**: System MUST provide a web chat interface accessible 24/7
- **FR-028**: System MUST display ticket ID prominently with ability to copy to clipboard
- **FR-029**: System MUST always display option to speak to a human (persistent "Talk to a Human" button in the application header)
- **FR-030**: System MUST provide high-contrast mode toggle for accessibility (WCAG 2.1 AA compliance), with system preference detection and persistence via localStorage
- **FR-031**: System MUST be responsive for mobile devices
- **FR-032**: System MUST show typing indicators during processing (client-side animation while awaiting response)
- **FR-033**: System MUST provide a My Tickets dashboard view where students can see all their tickets with status, department, priority, and timestamps in a master/detail layout
- **FR-034**: System MUST provide skip-to-content navigation, ARIA roles/labels on all interactive elements, keyboard navigation (Enter to send, Shift+Enter for newline), and a screen reader live region for chat messages

**Administration**

- **FR-035**: System MUST provide an admin dashboard for viewing, filtering (by status and department), updating, and deleting support tickets
- **FR-036**: System MUST allow administrators to update ticket status, assignee, and resolution notes
- **FR-037**: System MUST provide a branding configuration system allowing administrators to customize: institution logo URL, primary color, institution name, and tagline — with changes applied dynamically via CSS variables and live preview
- **FR-038**: System MUST provide a health check endpoint reporting per-service status (LLM, ticketing, knowledge base, session store)
- **FR-039**: System MUST provide a direct knowledge base search endpoint for querying articles by search term, department, and result limit

**Service Architecture**

- **FR-040**: System MUST implement a three-agent pipeline architecture: QueryAgent (intent analysis) → RouterAgent (routing decisions) → ActionAgent (ticket creation and KB retrieval), with each agent having bounded authority (QueryAgent CANNOT create tickets; RouterAgent CANNOT create tickets; ActionAgent CANNOT approve policies)
- **FR-041**: All external service integrations (LLM, ticketing, knowledge base, session store, audit log, branding) MUST be abstracted behind interfaces with a dependency injection container, supporting both mock and production implementations
- **FR-042**: System MUST support a mock mode for all services, enabling demo and development without external dependencies, controlled via a single configuration toggle
- **FR-043**: Deployment workflow MUST support non-interactive authentication using service principal credentials for both `az` and `azd`
- **FR-044**: Infrastructure templates MUST support separate `cosmosLocation` configuration so Cosmos DB can be provisioned in an alternate region when primary region capacity is unavailable
- **FR-045**: Infrastructure outputs MUST provide deploy-time service endpoints and resource group values required by validation scripts (`AZURE_CONTAINERAPP_URL`, `AZURE_RESOURCE_GROUP`)

### Non-Functional Requirements

- **NFR-001**: System MUST respond with ticket ID and initial guidance within 30 seconds
- **NFR-002**: System MUST be available 24/7 (target 99.9% uptime during pilot)
- **NFR-003**: System MUST support students: undergraduate, graduate, online, continuing education
- **NFR-004**: Session history MUST be retained for 90 days (TTL: 7,776,000 seconds) before anonymization for analytics. Persistent storage (e.g., Cosmos DB) is required for production; in-memory mock storage is acceptable for development/demo only.
- **NFR-005**: System MUST handle 500 concurrent users during peak registration periods. Rate limiting MUST be enforced (target: 100 requests per 60-second window per user).
- **NFR-006**: System MUST be containerized (Docker) with multi-stage builds and non-root user execution for security
- **NFR-007**: System MUST support deployment to Azure (Container Apps for backend, Static Web Apps for frontend) via Azure Developer CLI (azd) and Bicep infrastructure-as-code
- **NFR-008**: Deployment MUST complete non-interactively in CI or Codespaces environments using service principal credentials and without browser prompts
- **NFR-009**: Production deployment guidance MUST include mitigation steps for regional capacity failures (especially Cosmos DB) and provider registration blockers

### Key Entities

- **Session**: Represents a student's conversation context including session_id (UUID), student_id_hash (SHA-256, 64-char), creation timestamp, last activity timestamp, conversation_history (list of ConversationTurn, max 50 turns), clarification_attempts (0-3), and TTL (default 90 days)
- **ConversationTurn**: Represents a single turn in a conversation including turn_number, detected intent, routed department, ticket_id (if created), and timestamp
- **AuditLog**: Represents an immutable record of each interaction including log_id (UUID), timestamp, student_id_hash (64-char), session_id (UUID), detected_intent, confidence_score (0.0-1.0), routed_department, ticket_id, escalated (boolean), escalation_reason (required if escalated), pii_detected, sentiment, and response_time_ms
- **QueryResult**: Represents the output of intent analysis including detected intent (IntentCategory), confidence score (0.0-1.0), extracted entities (dict), pii_detected (boolean), pii_types (list), sentiment (Sentiment enum), urgency_indicators (list), and requires_escalation flag
- **RoutingDecision**: Represents the routing determination including target department (Department enum), priority (Priority enum), escalation flag with reason (EscalationReason enum), SLA (string), and needs_clarification flag
- **ActionResult**: Represents the outcome of executing a request including ticket_id, department, status (ActionStatus: created/escalated/pending_clarification/kb_only/error), knowledge_articles (list, max 3), estimated_response_time, escalation status, and user-facing message
- **KnowledgeArticle**: Represents a relevant help article including title, URL, and relevance score (0.0-1.0)
- **BrandingConfig**: Represents institution branding including logo_url, primary_color, institution_name, and tagline — applied dynamically via CSS variables

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: First-contact resolution rate improves from 40% to 65% (queries resolved without human transfer)
- **SC-002**: Students receive correct routing, ticket ID, and initial guidance within 30 seconds
- **SC-003**: System operates 24/7, handling after-hours requests that previously went unanswered
- **SC-004**: Average handling time decreases from 8 minutes to under 1 minute for standard requests
- **SC-005**: Student satisfaction score improves from 3.2/5 to 4.5/5 (post-interaction survey)
- **SC-006**: Escalation rate for automated decisions stays below 20%
- **SC-007**: Routing accuracy exceeds 90% (validated via human review of sample)
- **SC-008**: System correctly escalates 100% of policy-related requests (no unauthorized automated decisions)
- **SC-009**: PII is never exposed in logs or responses (100% compliance)

## Assumptions

- Students authenticate via existing university SSO before accessing the support agent (v1 uses a demo student stub for development/demo; production requires SSO integration)
- ServiceNow (or equivalent ticketing system) API is available for ticket creation (v1 uses mock implementation)
- University knowledge base content is available and indexed for search (v1 uses mock implementation with sample articles; production targets Azure AI Search)
- All external service integrations (ticketing, knowledge base, LLM) are abstracted behind interfaces with mock implementations for demo/testing mode
- Student ID can be obtained from authenticated session context
- Departments have defined SLAs that can be referenced for response time estimates
- v1 scope is English language only; multilingual support deferred to v2
- v1 scope is students only; faculty and staff support deferred to v2 and v3
- Azure OpenAI is the production LLM provider (accessed via REST API with httpx)
- Cosmos DB is the target production store for sessions, audit logs, and branding (v1 uses in-memory mocks)

## Dependencies

- University authentication system (SSO/OAuth) — **v1: demo stub**
- Ticketing system API (ServiceNow or equivalent) — **v1: mock implementation**
- Knowledge base and search infrastructure (Azure AI Search) — **v1: mock implementation**
- Session storage infrastructure for stateful conversations (Cosmos DB) — **v1: in-memory mock**
- Audit logging infrastructure (Cosmos DB) — **v1: in-memory mock**
- LLM service (Azure OpenAI) — **v1: production implementation available; mock fallback for offline dev**

## Clarifications

### Session 2026-01-20

- Q: What is the target concurrent user capacity during peak periods? → A: 500 concurrent users (mid-size university peak)
- Q: How should the system behave when SSO authentication is unavailable? → A: Allow read-only KB browsing; block ticket creation until authenticated
- Q: How should intent classification be implemented? → A: LLM-based classification with few-shot prompting (no training data needed)
- Q: Should external integrations support mock mode for demo/testing? → A: Yes, dual-mode with abstracted services and mock implementations
- Q: What format should ticket IDs use? → A: Structured format TKT-{DEPT}-{YYYYMMDD}-{SEQ} (e.g., TKT-IT-20260121-0042)

### Session 2026-02-06

- Q: Should the system always create a ticket for every query? → A: No. For LOW/MEDIUM priority queries where the knowledge base provides a highly relevant answer (relevance >= 0.5), the system may return KB articles without creating a ticket (KB-only self-service mode).
- Q: What administrative capabilities are needed? → A: Full ticket triage (list, filter by status/department, update status/assignee/resolution, delete) plus institution branding customization (logo, color, name, tagline) with live preview.
- Q: How should branding changes be applied? → A: Dynamically via CSS variables so changes take effect immediately without page reload.
- Q: What is the three-agent architecture? → A: QueryAgent (analyzes intent, extracts entities, detects PII/sentiment) → RouterAgent (routes to department, assigns priority, determines escalation) → ActionAgent (creates tickets, retrieves KB articles, generates response). Each agent has bounded authority and cannot perform actions outside its scope.

## Out of Scope (v1)

- Faculty and staff support (v2, v3)
- Multi-language support (v2)
- Proactive notifications ("Your transcript is ready")
- Sentiment-based crisis detection with automatic emergency escalation
- Integration with grant databases or research systems
- Voice/phone channel support
- Server-side streaming / real-time typing indicators (v1 uses client-side animation)
- Production SSO/OAuth middleware (v1 uses demo student stub)
- Production ServiceNow integration (v1 uses mock)
- Production Azure AI Search integration (v1 uses mock)
- Production Cosmos DB integration for sessions/audit/branding (v1 uses in-memory mocks)
- Rate limiting middleware enforcement (v1 has configuration only)
- Campus Safety department routing (no intent categories currently map to this department)

<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Bump rationale: MINOR — materially expanded 3 existing principles
  with voice/audio channel guidance; added voice-specific security
  constraints. No principles removed or fundamentally redefined.
Modified principles:
  - III. Privacy-First Data Handling → expanded with audio/voice PII rules
  - VI. Accessibility as Requirement → expanded with voice UI accessibility
  - VII. Graceful Degradation → expanded with WebRTC/Realtime API fallbacks
Added sections:
  - Voice Channel Security (under Security & Compliance Constraints)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check
    section exists; voice principles slot into existing gates)
  - .specify/templates/spec-template.md: ✅ Compatible (no structural
    changes required; voice stories use existing priority/scenario format)
  - .specify/templates/tasks-template.md: ✅ Compatible (voice tasks follow
    existing phase/checkpoint pattern)
Follow-up TODOs: None
-->

# Front Door Support Agent Constitution

## Core Principles

### I. Bounded Agent Authority (NON-NEGOTIABLE)

Each agent component MUST have explicitly defined boundaries enforced
architecturally:
- Agents MUST NOT have access to methods, services, or APIs that exceed
  their designated authority
- QueryAgent: Intent detection and entity extraction ONLY — no routing
  decisions, no ticket creation
- RouterAgent: Routing decisions ONLY — no intent detection, no ticket
  creation, no user communication
- ActionAgent: Ticket creation and knowledge retrieval ONLY — no approval
  methods, no record modification
- Voice tool calls MUST route through the same bounded pipeline — the
  Realtime API MUST NOT bypass agent boundaries via direct function access
- The absence of unauthorized capabilities MUST be enforced at the code
  level (methods simply do not exist)

**Rationale**: Architectural boundaries prevent scope creep and unauthorized
actions. If a method doesn't exist, it cannot be called — this is safer
than runtime permission checks. Voice as a new input modality MUST NOT
create a parallel authority path.

### II. Human Escalation for Policy Decisions (NON-NEGOTIABLE)

The system MUST escalate to human reviewers for any decision requiring
judgment, policy interpretation, or exception handling:
- Confidence score below 0.70 threshold
- Policy keywords detected (appeal, waiver, exception, override, refund,
  withdrawal deadline)
- Sensitive topics (Title IX, mental health, threats, discrimination)
- Multi-department coordination required
- User explicitly requests human contact
- Ambiguity unresolved after 3 clarification attempts
- Voice-originated escalations MUST include the PII-filtered transcript
  as context for the human reviewer

**Rationale**: Automated systems MUST NOT make decisions that affect student
rights, finances, or academic standing. Human judgment is required for
policy exceptions. Voice interactions carry the same escalation obligations
as text.

### III. Privacy-First Data Handling (NON-NEGOTIABLE)

All student data MUST be handled with privacy as the default:
- Student IDs MUST be hashed before storage in session and audit logs
- Raw query text containing PII MUST NOT be persisted beyond immediate
  processing
- Audit logs MUST capture intent and routing decisions without exposing
  sensitive content
- PII detection MUST flag queries for secure handling before any logging
  occurs
- Session history MUST store only PII-safe context (intents, ticket IDs,
  timestamps)

**Voice-specific obligations:**
- Raw audio MUST NOT be stored, cached, or persisted at any layer
- Only PII-filtered transcripts MAY be persisted
- The system MUST NOT repeat PII back to the user via synthesized speech
  (e.g., if a student says their SSN, the agent MUST NOT echo it)
- PII filtering MUST occur at three layers: (1) Realtime API system
  instructions, (2) backend transcript filter before persistence,
  (3) post-processing scrub before audit log entry
- Voice transcripts MUST be treated with the same PII handling as typed
  text — no lower standard for spoken input
- Ephemeral session tokens for WebRTC MUST expire and MUST NOT be reusable

**Rationale**: FERPA compliance and student trust require that personal
information is protected by design, not by policy alone. Audio is a
higher-risk modality because users may inadvertently speak sensitive
information they would not type.

### IV. Stateful Context Preservation

The system MUST maintain conversation context across multi-turn
interactions:
- Session state MUST persist student context, conversation history, and
  ticket references
- Follow-up queries ("What's the status of my ticket?") MUST resolve
  without re-authentication
- Session data MUST be retained for 90 days before anonymization for
  analytics
- Graceful degradation MUST occur if session storage is unavailable
  (inform user, continue stateless)
- Voice and text interactions MUST share the same session context —
  switching modality MUST NOT lose conversation state
- Voice transcripts MUST be appended to the shared chat thread with
  `input_modality="voice"` annotation

**Rationale**: Students should not need to re-explain their situation.
Stateful design enables natural conversation and reduces frustration.
Modality switching (voice ↔ text) MUST be seamless.

### V. Test-First Development

All agent behaviors MUST be validated through tests written before
implementation:
- Acceptance scenarios from the spec MUST be converted to executable tests
- Intent detection MUST be tested against the defined query-to-intent
  mappings
- Escalation triggers MUST be tested to ensure 100% of policy queries
  escalate
- Boundary violations MUST be tested (attempting unauthorized actions
  should fail)
- Voice-specific tests MUST cover: PII filtering of spoken input,
  tool call relay accuracy, degradation to text mode, and session
  sharing between modalities

**Rationale**: Agent systems have high stakes for incorrect behavior.
Test-first ensures behaviors are verified, not assumed. Voice adds
additional attack surface that MUST be tested.

### VI. Accessibility as Requirement

The user interface MUST meet accessibility standards as functional
requirements, not afterthoughts:
- WCAG AA compliance MUST be achieved; AAA for high-contrast mode
- All interactive elements MUST be keyboard navigable
- Screen reader compatibility MUST be validated
- Mobile responsiveness MUST be tested on actual devices

**Voice-specific obligations:**
- The microphone toggle MUST be keyboard accessible (Space/Enter)
- Voice state changes (listening, processing, speaking, error) MUST be
  announced via ARIA live regions for screen reader users
- Visual state indicators MUST accompany all voice states (not audio-only
  feedback)
- When voice is unavailable, the text fallback MUST be clearly
  communicated to the user
- Voice UI MUST NOT be the only path to any functionality — text MUST
  always be available as an alternative

**Rationale**: University services must be accessible to all students.
Accessibility is a legal requirement (ADA/Section 508) and an ethical
imperative. Voice features MUST enhance accessibility, not create
new barriers.

### VII. Graceful Degradation

The system MUST continue providing value when external dependencies fail:
- If ticketing system is unavailable: Log request for retry, inform user,
  provide KB articles
- If knowledge base is unavailable: Create ticket, inform user help
  articles temporarily unavailable
- If LLM service is unavailable: Provide fallback routing based on
  keyword matching, escalate to human
- All degradation states MUST be logged for operational visibility

**Voice-specific degradation:**
- If Azure OpenAI Realtime API is unavailable: Fall back to text-only
  mode with a clear user message, preserve all session context
- If WebRTC connection fails mid-conversation: Display "Connection lost"
  message, preserve transcript and context, allow seamless switch to text
- If microphone permission is denied: Hide voice controls, guide user
  to text input, do not block the chat experience
- If VAD (Voice Activity Detection) malfunctions: Fall back to push-to-
  talk or text mode
- Mock mode MUST provide full voice UX without any Azure credentials
  for development and demo purposes

**Rationale**: 24/7 availability is a core promise. Partial functionality
is better than complete failure. Voice is an enhancement — its absence
MUST NOT degrade the existing text experience.

## Security & Compliance Constraints

### Data Access Boundaries
- System MUST NOT access FERPA-protected student records beyond routing
  context
- System MUST NOT store financial data (account numbers, SSN, payment info)
- System MUST NOT retain health information beyond routing to appropriate
  support

### Integration Security
- All external API calls MUST use authenticated, encrypted connections
- API credentials MUST NOT be stored in code or logs
- Rate limiting MUST be implemented on all endpoints

### Voice Channel Security
- Ephemeral tokens for WebRTC sessions MUST have short TTL (≤60 seconds)
  and MUST NOT be reusable
- The WebSocket relay (`/api/realtime/ws`) MUST validate session ownership
  before executing tool calls
- Audio data MUST NOT transit through the backend — WebRTC connects
  directly from browser to Azure OpenAI
- Tool call results relayed via WebSocket MUST be PII-filtered before
  reaching the client
- All voice session events MUST include `input_modality="voice"` in
  audit log entries
- The system MUST NOT expose Azure OpenAI API keys to the frontend —
  only ephemeral tokens

### Audit Requirements
- All routing decisions MUST be logged with timestamp, intent, department,
  and escalation status
- Audit logs MUST be immutable (append-only)
- Logs MUST be retained per university data retention policy (minimum
  7 years for FERPA)
- Voice audit entries MUST include: session_id, input_modality, tool
  calls invoked, PII_detected flag, and degradation events

## Development Workflow

### Code Review Requirements
- All changes MUST be reviewed before merge
- Reviewer MUST verify Constitution compliance (boundary enforcement,
  escalation triggers, privacy handling)
- Security-sensitive changes MUST have security-focused review
- Voice feature changes MUST include PII and degradation review

### Quality Gates
- All tests MUST pass before merge
- Code coverage MUST not decrease
- Accessibility tests MUST pass for UI changes
- Performance benchmarks MUST meet <30 second response time requirement
- Voice-specific: PII filtering tests MUST pass, degradation tests
  MUST pass, accessibility tests for voice UI MUST pass

### Documentation Standards
- API contracts MUST be documented in OpenAPI format
- Agent boundaries MUST be documented in code comments
- Escalation rules MUST be documented and version-controlled
- Voice endpoints and WebSocket protocol MUST be documented

## Governance

This Constitution establishes non-negotiable principles for the Front Door
Support Agent. All development decisions MUST comply with these principles.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Review against existing principles for conflicts
3. Update version number per semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle or material expansion of existing guidance
   - PATCH: Clarifications, wording improvements, non-semantic changes
4. Update dependent templates if affected
5. Document migration plan for existing code if breaking change

### Compliance Verification
- All pull requests MUST include Constitution compliance checklist
- Quarterly review of system behavior against principles
- Incident post-mortems MUST assess Constitution adherence

### Conflict Resolution
- Constitution principles take precedence over convenience or speed
- When principles conflict, prioritize:
  Privacy > Security > Human Escalation > User Experience
- Document conflicts and resolutions in decision log

**Version**: 1.1.0 | **Ratified**: 2026-01-20 | **Last Amended**: 2026-03-13

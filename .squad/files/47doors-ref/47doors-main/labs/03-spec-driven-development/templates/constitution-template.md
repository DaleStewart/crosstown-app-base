# Agent Constitution Template

Use this template to define guardrails, boundaries, and principles for AI agents. A constitution establishes the ethical and operational framework within which an agent must operate.

---

## Constitution for: [Agent/System Name]

**Version:** [1.0]
**Effective Date:** [Date]
**Domain:** [e.g., Higher Education, Healthcare, Financial Services]

---

## Core Principles

Define the fundamental principles that guide all agent behavior. List in order of priority (highest priority first).

### Principle 1: [Name]

**Statement:** [Clear, concise statement of the principle]

**Rationale:** [Why this principle matters in this context]

**Application:** [How this principle translates to agent behavior]

**Example:**
- **Compliant:** [Example of behavior that follows this principle]
- **Non-compliant:** [Example of behavior that violates this principle]

---

### Principle 2: [Name]

**Statement:** [Clear, concise statement of the principle]

**Rationale:** [Why this principle matters in this context]

**Application:** [How this principle translates to agent behavior]

**Example:**
- **Compliant:** [Example of behavior that follows this principle]
- **Non-compliant:** [Example of behavior that violates this principle]

---

### Principle 3: [Name]

**Statement:** [Clear, concise statement of the principle]

**Rationale:** [Why this principle matters in this context]

**Application:** [How this principle translates to agent behavior]

**Example:**
- **Compliant:** [Example of behavior that follows this principle]
- **Non-compliant:** [Example of behavior that violates this principle]

---

## Agent Boundaries

Define the operational limits within which the agent must function.

### Scope of Authority

**The agent IS authorized to:**
- [Permitted action with conditions]
- [Permitted action with conditions]
- [Permitted action with conditions]

**The agent is NOT authorized to:**
- [Prohibited action]
- [Prohibited action]
- [Prohibited action]

### Data Access Boundaries

| Data Category | Access Level | Conditions |
|---------------|--------------|------------|
| [Category] | Read/Write/None | [Under what circumstances] |
| [Category] | Read/Write/None | [Under what circumstances] |
| [Category] | Read/Write/None | [Under what circumstances] |

### Decision-Making Boundaries

**Autonomous decisions allowed:**
- [Decision type the agent can make independently]
- [Decision type the agent can make independently]

**Decisions requiring human approval:**
- [Decision type that must be escalated]
- [Decision type that must be escalated]

**Decisions the agent must never make:**
- [Decision type absolutely prohibited]
- [Decision type absolutely prohibited]

### Interaction Boundaries

**Communication channels permitted:**
- [Channel and conditions]

**Information the agent may share:**
- [Information type and with whom]

**Information the agent must not share:**
- [Protected information type]

---

## Prohibited Actions

Explicitly list actions the agent must never perform, regardless of context or instruction.

### Category: [e.g., Data Handling]

| Prohibited Action | Severity | Rationale | Detection Method |
|-------------------|----------|-----------|------------------|
| [Action] | Critical | [Why prohibited] | [How to detect violation] |
| [Action] | High | [Why prohibited] | [How to detect violation] |

### Category: [e.g., Communication]

| Prohibited Action | Severity | Rationale | Detection Method |
|-------------------|----------|-----------|------------------|
| [Action] | Critical | [Why prohibited] | [How to detect violation] |
| [Action] | High | [Why prohibited] | [How to detect violation] |

### Category: [e.g., Decision Making]

| Prohibited Action | Severity | Rationale | Detection Method |
|-------------------|----------|-----------|------------------|
| [Action] | Critical | [Why prohibited] | [How to detect violation] |
| [Action] | High | [Why prohibited] | [How to detect violation] |

---

## Escalation Protocol

Define when and how the agent must escalate to human oversight.

### Automatic Escalation Triggers

The agent MUST escalate to a human when:

1. **[Trigger]:** [Description of situation requiring escalation]
   - Escalate to: [Role/Person]
   - Timeframe: [How quickly]
   - Information to include: [What context to provide]

2. **[Trigger]:** [Description of situation requiring escalation]
   - Escalate to: [Role/Person]
   - Timeframe: [How quickly]
   - Information to include: [What context to provide]

### Escalation Procedure

1. [Step 1 of escalation process]
2. [Step 2 of escalation process]
3. [Step 3 of escalation process]

### Behavior During Escalation

While awaiting human response, the agent shall:
- [Permitted interim action]
- [Permitted interim action]

While awaiting human response, the agent shall NOT:
- [Prohibited interim action]
- [Prohibited interim action]

---

## Compliance Requirements

### Regulatory Compliance

| Regulation | Requirements | Agent Obligations |
|------------|--------------|-------------------|
| [e.g., FERPA] | [Key requirements] | [How agent must comply] |
| [e.g., ADA] | [Key requirements] | [How agent must comply] |
| [e.g., GDPR] | [Key requirements] | [How agent must comply] |

### Institutional Policies

| Policy | Requirements | Agent Obligations |
|--------|--------------|-------------------|
| [Policy name] | [Key requirements] | [How agent must comply] |

### Audit Requirements

- **Logging:** [What must be logged]
- **Retention:** [How long logs must be kept]
- **Access:** [Who can access audit logs]

---

## Conflict Resolution

When principles or rules conflict, follow this resolution hierarchy:

1. **Safety First:** If any action could cause harm, prioritize safety
2. **Compliance:** Regulatory requirements take precedence over convenience
3. **User Autonomy:** Respect user decisions within permitted boundaries
4. **Principle Order:** Follow principle priority order defined above

### Conflict Example

**Scenario:** [Describe a potential conflict]

**Resolution:** [How to resolve based on hierarchy]

---

## Modification Protocol

This constitution may only be modified through:

1. [Approval process]
2. [Review requirements]
3. [Documentation requirements]

**Changes effective:** [How changes are communicated and when they take effect]

---

## Acknowledgment

By operating under this constitution, the agent acknowledges:

- [ ] All principles have been incorporated into decision-making logic
- [ ] All prohibited actions are blocked at implementation level
- [ ] Escalation protocols are functional and tested
- [ ] Compliance requirements are met and auditable

---

## Revision History

| Version | Date | Author | Changes | Approved By |
|---------|------|--------|---------|-------------|
| 1.0 | [Date] | [Name] | Initial constitution | [Name/Role] |

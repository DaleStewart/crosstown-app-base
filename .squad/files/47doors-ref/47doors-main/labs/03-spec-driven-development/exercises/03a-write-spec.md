# Exercise 03a: Write a Spec for the Escalation Detection Agent

**Duration:** 25 minutes

## Overview

In this exercise, you will write a complete specification for an **Escalation Detection Agent**. This agent monitors student communications and interactions to identify situations that may require human intervention, such as academic distress, accessibility needs, or urgent support requests.

## Learning Objectives

- Practice writing clear, implementable specifications
- Define user stories from multiple stakeholder perspectives
- Create measurable success criteria
- Document constraints and boundaries

## Background: The Escalation Detection Agent

Higher education institutions receive thousands of student communications daily. Some of these communications contain signals that require urgent human attention:

- A student expressing academic distress or mental health concerns
- Requests for disability accommodations
- Complaints about discrimination or harassment
- Financial aid emergencies
- Safety concerns

The Escalation Detection Agent will analyze incoming communications and flag those requiring human review, categorize them by urgency and type, and route them to appropriate staff.

## Instructions

### Part 1: Create Your Specification (15 minutes)

1. Create a new file called `your-spec.md` in the lab directory
2. Use the template from `templates/spec-template.md` as your starting point
3. Complete each section for the Escalation Detection Agent

#### Required Sections

**Feature Name:**
Name your feature clearly (e.g., "Escalation Detection Agent" or similar)

**User Stories (minimum 3):**

Write user stories from these perspectives:

1. **Student Perspective:** A student who needs their urgent concern addressed quickly
2. **Advisor/Staff Perspective:** A staff member who needs to prioritize their response queue
3. **System/Admin Perspective:** An administrator who needs oversight and reporting

**Functional Requirements (minimum 5):**

Consider these categories:
- Input processing (what data does the agent receive?)
- Detection logic (how does it identify escalation signals?)
- Classification (what categories of escalation exist?)
- Routing (how are flagged items assigned?)
- Notification (how are humans alerted?)

**Success Criteria:**

Define measurable criteria such as:
- Detection accuracy (precision/recall targets)
- Response time requirements
- False positive/negative thresholds
- Coverage requirements

**Constraints:**

Address these constraint categories:
- Technical (language, framework, dependencies)
- Compliance (FERPA, accessibility)
- Operational (what the agent cannot do)

### Part 2: Create Your Constitution (10 minutes)

1. Create a new file called `your-constitution.md` in the lab directory
2. Use the template from `templates/constitution-template.md` as your starting point
3. Complete the following sections for the Higher Education context

#### Required Sections

**Core Principles (minimum 3):**

Consider principles like:
- Student privacy and dignity
- Human oversight for sensitive decisions
- Transparency in automated decisions
- Avoiding bias and discrimination

**Agent Boundaries:**

Define what the agent:
- IS authorized to do
- Is NOT authorized to do
- Must escalate to humans

**Prohibited Actions:**

List actions the agent must NEVER perform:
- Related to student data
- Related to automated decisions
- Related to communication

**Compliance Requirements:**

Address:
- FERPA (student records privacy)
- ADA/Accessibility
- Institutional policies

## Example Content

Here's an example user story to guide your writing:

> **Story: Urgent Mental Health Concern**
>
> As a **student in crisis**,
> I want **my message about struggling mentally to be flagged for immediate human review**
> So that **I receive timely support from a counselor rather than an automated response**
>
> **Acceptance Criteria:**
> - [ ] Messages containing mental health keywords are flagged within 30 seconds
> - [ ] Flagged messages are routed to counseling services queue
> - [ ] Student receives acknowledgment that their message is being prioritized
> - [ ] Human counselor is notified via urgent alert

Here's an example prohibited action:

| Prohibited Action | Severity | Rationale |
|-------------------|----------|-----------|
| Responding to mental health concerns without human review | Critical | Students in crisis need human support; automated responses could cause harm |
| Sharing escalation reasons with other students | Critical | Violates student privacy and could cause stigmatization |

## Validation Checklist

Before moving to Exercise 03b, verify your spec:

- [ ] Feature name is clear and descriptive
- [ ] At least 3 user stories with acceptance criteria
- [ ] At least 5 functional requirements with priorities
- [ ] Success criteria are measurable (include numbers/percentages)
- [ ] Constraints address FERPA and accessibility
- [ ] At least 2 concrete examples with inputs/outputs

Verify your constitution:

- [ ] At least 3 core principles in priority order
- [ ] Agent boundaries clearly define permitted vs. prohibited actions
- [ ] Prohibited actions include rationale
- [ ] Escalation protocol is defined
- [ ] FERPA compliance is addressed

## Tips for Writing Effective Specs

1. **Be Specific:** Instead of "fast response time," write "response time < 500ms for 95th percentile"

2. **Include Edge Cases:** What happens when:
   - A message contains multiple escalation signals?
   - The confidence score is borderline?
   - The routing queue is full?

3. **Define "Not" as much as "Is":** Explicitly state what the feature will NOT do

4. **Use Consistent Terminology:** Define terms like "escalation," "urgent," "flag" and use them consistently

5. **Consider Failure Modes:** What happens when detection fails? What's the fallback?

### Extension: Voice-Aware Specification

When writing specs for agents that may be accessed via voice, consider adding these constraints:
- **Response length** — spoken responses should be 2–3 sentences max
- **Phonetic clarity** — IDs and codes should be spelled out ("T-K-T dash I-T dash 0-0-4-2")
- **PII handling** — never echo back sensitive data the caller provides
- **Silence handling** — what happens when the caller stops talking? (VAD timeout)

Try adding a "Voice Modality" section to your Escalation Detection Agent spec that addresses these constraints.

## Deliverables

When complete, you should have:

1. `your-spec.md` - Complete feature specification
2. `your-constitution.md` - Complete agent constitution

## Next Steps

Once your spec and constitution are complete, proceed to [Exercise 03b: Generate from Spec](03b-generate-from-spec.md) to use Copilot to generate code from your specifications.

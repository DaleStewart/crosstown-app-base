# Multi-Agent Design

## Goal

Design a support workflow that classifies user requests, routes them safely, and executes the right action with traceable outputs.

## Components

1. QueryAgent

- Input: user message and recent context.
- Output: intent, confidence, entities.
- Responsibility: understanding only.

2. RouterAgent

- Input: structured output from QueryAgent.
- Output: target specialist, priority, and rationale.
- Responsibility: decision policy and branching.

3. Action Specialists

- RetrieveAgent for knowledge lookups with citations.
- TicketAgent for issue creation and status tracking.
- EscalationAgent for policy-sensitive or urgent requests.
- GeneralAgent for small talk and low-risk replies.

4. Orchestrator

- Maintains session state.
- Executes stage sequence.
- Handles retries and fallbacks.
- Emits logs and metrics.

## Data Flow Diagram

```text
User Message
   |
   v
+-----------+
| QueryAgent|
+-----------+
   |
   v
+-----------+
| Router    |
| Agent     |
+-----------+
   |
   +--------------------+
   |                    |
   v                    v
+-------------+    +---------------+
| Retrieve    |    | Ticket / Esc  |
| Specialist  |    | Specialist    |
+-------------+    +---------------+
   |                    |
   +----------+---------+
              |
              v
         +-----------+
         | Response  |
         | to User   |
         +-----------+
```

## Design Notes

- The router uses threshold-based branching: low confidence routes to clarification.
- Specialists are isolated so prompt tuning does not leak across concerns.
- The orchestrator records stage latency and failure reasons for troubleshooting.
- A safe fallback always exists when a specialist tool fails.

## Why this helps

This approach reduces regression risk, improves explainability, and lets teams ship iterative changes quickly. Each role has a narrow contract, so tests are straightforward and failures are localized.

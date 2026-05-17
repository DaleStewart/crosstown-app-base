# Lab 05 - Agent Orchestration: Completion Specification

## What "Done" Looks Like

Lab 05 is complete when you have built a working three-agent orchestration pipeline that processes user queries through QueryAgent, RouterAgent, and ActionAgent stages, with support for multi-turn conversations. You should be able to:

1. Process any user message through the complete pipeline and receive an appropriate response
2. Maintain conversation context across multiple turns in the same session
3. Route different intents to specialized ActionAgents based on classification
4. Handle errors gracefully with fallback agents

A successfully completed Lab 05 means you have a functional agent orchestration system ready for deployment, with clear handoff protocols and session state management.

---

## Checkable Deliverables

### 1. Full Pipeline QueryAgent -> RouterAgent -> ActionAgent Working

**What it verifies:**
- All three agents are implemented and connected
- Data flows correctly between agents using defined contracts
- The pipeline produces coherent responses for various input types
- Handoff protocols preserve necessary context

**Acceptance Criteria:**
- [ ] QueryAgent parses user messages into StructuredQuery objects
- [ ] StructuredQuery includes intent classification with confidence score
- [ ] Entity extraction identifies relevant entities (names, IDs, topics)
- [ ] RouterAgent maps intents to correct ActionAgents
- [ ] Routing decision includes reasoning and fallback agent
- [ ] At least 3 ActionAgents implemented (Retrieve, General, Escalation)
- [ ] Pipeline returns AgentResponse with content and metadata
- [ ] End-to-end latency under 5 seconds for typical queries

**How to Test:**

```bash
# Run pipeline integration tests
python -m pytest tests/test_pipeline.py -v
```

**Test Cases:**

| Input | Expected Flow | Expected Outcome |
|-------|---------------|------------------|
| "Hello!" | Query -> Router -> General | Friendly greeting response |
| "How do I reset my password?" | Query -> Router -> Retrieve | KB answer with citations |
| "Check ticket TKT-12345" | Query -> Router -> Ticket | Ticket status (or mock) |
| "I need to talk to someone" | Query -> Router -> Escalation | Human handoff message |
| "asdfghjkl" | Query -> Router -> Clarification | Request for clarification |

**Verification Script:**

```python
# test_pipeline.py
import pytest
from pipeline import AgentPipeline
from models import Intent

@pytest.mark.asyncio
async def test_pipeline_processes_greeting():
    """Verify pipeline handles simple greeting."""
    pipeline = AgentPipeline(...)
    response, session_id = await pipeline.process("Hello there!")

    assert response.content, "Should return non-empty response"
    assert response.confidence > 0.5, "Should have reasonable confidence"
    assert session_id, "Should return session ID"

@pytest.mark.asyncio
async def test_pipeline_routes_knowledge_query():
    """Verify knowledge queries go to RetrieveAgent."""
    pipeline = AgentPipeline(...)
    response, _ = await pipeline.process("What is the vacation policy?")

    # Should have sources if RAG is working
    # (may be empty if KB doesn't have this topic)
    assert response.content, "Should return response"

@pytest.mark.asyncio
async def test_pipeline_handles_escalation():
    """Verify escalation requests are handled."""
    pipeline = AgentPipeline(...)
    response, _ = await pipeline.process("I need to speak to a human agent")

    assert "human" in response.content.lower() or \
           "agent" in response.content.lower() or \
           "support" in response.content.lower(), \
           "Should acknowledge escalation request"

@pytest.mark.asyncio
async def test_pipeline_handles_unknown_intent():
    """Verify unclear queries get clarification."""
    pipeline = AgentPipeline(...)
    response, _ = await pipeline.process("xyz123 foo bar")

    assert response.requires_followup or \
           "clarif" in response.content.lower() or \
           "understand" in response.content.lower(), \
           "Should request clarification for unclear input"

@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Verify pipeline handles errors gracefully."""
    pipeline = AgentPipeline(...)

    # Even with bad input, should not throw
    response, session_id = await pipeline.process("")

    assert response is not None, "Should return response even for edge cases"
    assert session_id, "Should still create/maintain session"
```

---

### 2. Multi-Turn Conversation Works

**What it verifies:**
- Session state is maintained across conversation turns
- Previous context influences subsequent responses
- Entity information persists within session
- Conversation history is available to agents

**Acceptance Criteria:**
- [ ] Session ID is generated and returned on first turn
- [ ] Same session ID used for subsequent turns maintains state
- [ ] Conversation history (last 5 turns) available in session
- [ ] Extracted entities persist across turns
- [ ] Agents can reference previous conversation context
- [ ] Session can be explicitly ended/cleared
- [ ] Context summary accurately reflects conversation state

**How to Test:**

```bash
# Run session management tests
python -m pytest tests/test_session.py -v
```

**Test Cases:**

| Scenario | Verification |
|----------|--------------|
| Turn 1: "My name is Alice" -> Turn 2: "What's my name?" | Should reference "Alice" |
| Turn 1: KB query -> Turn 2: "Tell me more" | Should understand context |
| Turn 1: Ticket question -> Turn 2: Same topic follow-up | Should not re-ask for ticket ID |
| 3 turns of conversation | Session should have 3 turns recorded |
| New session | Should start fresh, no history |

**Verification Script:**

```python
# test_session.py
import pytest
from session import Session, SessionManager
from pipeline import AgentPipeline

@pytest.mark.asyncio
async def test_session_maintains_history():
    """Verify conversation history is recorded."""
    pipeline = AgentPipeline(...)

    # Turn 1
    _, session_id = await pipeline.process("Hello")

    # Turn 2
    await pipeline.process("How are you?", session_id)

    # Check session
    session = pipeline.session_manager.get(session_id)
    assert len(session.turns) == 2, "Should have 2 turns recorded"

@pytest.mark.asyncio
async def test_context_influences_response():
    """Verify context from previous turns influences responses."""
    pipeline = AgentPipeline(...)

    # Turn 1: Establish context
    _, session_id = await pipeline.process(
        "I'm having trouble with my email password"
    )

    # Turn 2: Follow-up without restating context
    response, _ = await pipeline.process(
        "Can you help me fix it?",
        session_id
    )

    # Response should relate to password/email issue
    assert any(word in response.content.lower()
               for word in ["password", "email", "reset", "account"]), \
           "Should reference previous context"

@pytest.mark.asyncio
async def test_entity_persistence():
    """Verify entities are remembered across turns."""
    pipeline = AgentPipeline(...)

    # Turn 1: Provide entity
    _, session_id = await pipeline.process(
        "My ticket number is TKT-12345"
    )

    # Get session and check entities
    session = pipeline.session_manager.get(session_id)
    all_entities = {}
    for turn in session.turns:
        all_entities.update(turn.entities)

    assert "ticket_id" in all_entities or "TKT-12345" in str(all_entities), \
           "Should extract and store ticket ID"

@pytest.mark.asyncio
async def test_new_session_is_fresh():
    """Verify new sessions have no history."""
    pipeline = AgentPipeline(...)

    # Create first session with some context
    _, session_id_1 = await pipeline.process("My name is Bob")
    await pipeline.process("I work in IT", session_id_1)

    # Create new session
    _, session_id_2 = await pipeline.process("Hello")

    assert session_id_1 != session_id_2, "Should be different sessions"

    session_2 = pipeline.session_manager.get(session_id_2)
    assert len(session_2.turns) == 1, "New session should have only 1 turn"

@pytest.mark.asyncio
async def test_get_history_limits_turns():
    """Verify history retrieval respects max_turns."""
    session = Session()

    # Add 10 turns
    for i in range(10):
        session.add_turn(
            user_message=f"Message {i}",
            agent_response=f"Response {i}",
            intent="general_chat",
            entities={}
        )

    # Get last 5
    history = session.get_history(max_turns=5)

    # Should have 10 items (5 user + 5 assistant)
    assert len(history) == 10, "Should return 5 turns (10 messages)"

@pytest.mark.asyncio
async def test_context_summary_generation():
    """Verify context summary is meaningful."""
    session = Session()

    session.add_turn(
        user_message="How do I reset my password?",
        agent_response="Here's how...",
        intent="knowledge_query",
        entities={"topic": "password"}
    )

    session.add_turn(
        user_message="What about my ticket TKT-123?",
        agent_response="Let me check...",
        intent="ticket_status",
        entities={"ticket_id": "TKT-123"}
    )

    summary = session.get_context_summary()

    assert "knowledge_query" in summary or "ticket_status" in summary, \
           "Summary should mention recent intents"
    assert "TKT-123" in summary or "ticket_id" in summary, \
           "Summary should mention extracted entities"
```

---

## Verification Steps

### Step 1: Agent Implementation Verification

```bash
# 1. Verify all agent files exist and are importable
python -c "from query_agent import QueryAgent; print('QueryAgent OK')"
python -c "from router_agent import RouterAgent; print('RouterAgent OK')"
python -c "from action_agents import RetrieveAgent, GeneralAgent, EscalationAgent; print('ActionAgents OK')"
python -c "from pipeline import AgentPipeline; print('Pipeline OK')"

# Expected: All imports succeed without errors
```

### Step 2: Pipeline Flow Verification

```bash
# Run the pipeline test suite
python -m pytest tests/test_pipeline.py -v --tb=short

# Expected output:
# test_pipeline.py::test_pipeline_processes_greeting PASSED
# test_pipeline.py::test_pipeline_routes_knowledge_query PASSED
# test_pipeline.py::test_pipeline_handles_escalation PASSED
# test_pipeline.py::test_pipeline_handles_unknown_intent PASSED
# test_pipeline.py::test_pipeline_error_handling PASSED
```

### Step 3: Session Management Verification

```bash
# Run session tests
python -m pytest tests/test_session.py -v --tb=short

# Expected output:
# test_session.py::test_session_maintains_history PASSED
# test_session.py::test_context_influences_response PASSED
# test_session.py::test_entity_persistence PASSED
# test_session.py::test_new_session_is_fresh PASSED
# test_session.py::test_get_history_limits_turns PASSED
# test_session.py::test_context_summary_generation PASSED
```

### Step 4: Multi-Turn Conversation Manual Test

```python
# Run interactive multi-turn test
python test_pipeline.py

# Expected sample output:
# ============================================================
# Turn 1
# User: Hi there!
# ------------------------------------------------------------
# Agent: Hello! How can I help you today?
# Confidence: 0.85
#
# ============================================================
# Turn 2
# User: How do I reset my password?
# ------------------------------------------------------------
# Agent: To reset your password, follow these steps [1]:
# 1. Go to the login page...
# Confidence: 0.90
# Sources: ['Password Reset Procedure']
#
# ============================================================
# Turn 3
# User: What if that doesn't work?
# ------------------------------------------------------------
# Agent: If the standard reset process doesn't work [1], you can...
# (Response should reference previous password context)
```

---

## Assessment Rubric

### Total Points: 25 (Agent Orchestration)

| Criteria | Points | Description |
|----------|--------|-------------|
| **QueryAgent Implementation** | 5 | Correctly parses and classifies user messages |
| **RouterAgent Implementation** | 5 | Routes to correct agents with proper fallbacks |
| **ActionAgent Implementation** | 5 | At least 3 working ActionAgents |
| **Pipeline Orchestration** | 5 | Full flow works end-to-end with error handling |
| **Session Management** | 5 | Multi-turn context maintained correctly |

### Detailed Scoring Guide

#### QueryAgent Implementation (5 points)
- **5 points:** Extracts intent, entities, confidence; handles edge cases; uses session context
- **4 points:** Works for common cases but misses some entities or edge cases
- **3 points:** Basic intent classification works but entity extraction incomplete
- **2 points:** Returns structured output but classification unreliable
- **0-1 points:** Not functional or returns invalid data

#### RouterAgent Implementation (5 points)
- **5 points:** Correct routing for all intents; fallback logic works; handles low confidence
- **4 points:** Routing works but missing fallback for some cases
- **3 points:** Basic routing works but doesn't handle ambiguous queries
- **2 points:** Only routes some intents correctly
- **0-1 points:** Routing mostly fails or hardcoded

#### ActionAgent Implementation (5 points)
- **5 points:** 3+ agents, all work correctly, proper response format, citations where applicable
- **4 points:** 3 agents work but minor issues (missing citations, etc.)
- **3 points:** 2 agents work well, third has issues
- **2 points:** Only 1-2 agents partially functional
- **0-1 points:** ActionAgents not functional

#### Pipeline Orchestration (5 points)
- **5 points:** Full flow works, error handling, logging, graceful degradation
- **4 points:** Pipeline works but error handling incomplete
- **3 points:** Works for happy path but fails on edge cases
- **2 points:** Partial flow works but some stages broken
- **0-1 points:** Pipeline not connected or mostly broken

#### Session Management (5 points)
- **5 points:** History tracked, context influences responses, entities persist, cleanup works
- **4 points:** Sessions work but context not fully utilized
- **3 points:** Basic session tracking but history not used effectively
- **2 points:** Sessions created but state not maintained properly
- **0-1 points:** No session management or broken

---

## Common Failure Modes and Resolutions

### Intent Classification Inconsistent

**Symptom:** Same query classified differently on repeated runs

**Resolution:**
```python
# Use lower temperature for deterministic classification
response = await client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.0,  # Deterministic
    response_format={"type": "json_object"}  # Structured output
)

# Add explicit examples in system prompt
system_prompt = """...
Examples:
- "How do I reset my password?" -> intent: knowledge_query
- "Hi there!" -> intent: general_chat
- "I need to speak to someone" -> intent: escalation
..."""
```

---

### Router Sends to Wrong Agent

**Symptom:** Knowledge queries go to GeneralAgent instead of RetrieveAgent

**Resolution:**
```python
# Check routing table mapping
ROUTING_TABLE = {
    Intent.KNOWLEDGE_QUERY: ("retrieve_agent", "general_agent"),  # Primary, Fallback
    # ... ensure all intents mapped
}

# Add logging to debug
logger.debug(f"Query intent: {query.intent}")
logger.debug(f"Routing decision: {decision.target_agent}")
logger.debug(f"Routing reasoning: {decision.reasoning}")
```

---

### Session Context Not Used

**Symptom:** Agent doesn't reference previous conversation

**Resolution:**
```python
# Ensure history is passed to agent prompts
history = session.get_history(max_turns=5)

messages = [
    {"role": "system", "content": system_prompt},
    *history,  # Previous turns
    {"role": "user", "content": current_message}
]

# Include context summary
context = session.get_context_summary()
user_prompt = f"""Previous context: {context}

Current question: {current_message}"""
```

---

### ActionAgent Throws Exception

**Symptom:** Pipeline returns error response or crashes

**Resolution:**
```python
# Add error handling in pipeline
async def _execute_action(self, decision, session):
    agent = self.action_agents.get(decision.target_agent)

    if not agent:
        logger.error(f"No agent found: {decision.target_agent}")
        agent = self.action_agents["general_agent"]

    try:
        return await agent.execute(decision, session)
    except Exception as e:
        logger.exception(f"Agent {decision.target_agent} failed")

        # Try fallback
        if decision.fallback_agent:
            fallback = self.action_agents.get(decision.fallback_agent)
            if fallback:
                return await fallback.execute(decision, session)

        # Return error response
        return AgentResponse(
            content="I encountered an issue. Please try again.",
            confidence=0.0
        )
```

---

### Entities Lost Between Turns

**Symptom:** Agent asks for ticket ID again even though user provided it

**Resolution:**
```python
# Ensure entities are stored in session
session.add_turn(
    user_message=user_message,
    agent_response=response.content,
    intent=structured_query.intent.value,
    entities=structured_query.entities  # Must include extracted entities
)

# In subsequent turns, check session for known entities
def _build_parameters(self, query: StructuredQuery, session: Session) -> dict:
    params = {"query": query.original_text}

    # Merge entities from current query and session history
    all_entities = {}
    for turn in session.turns:
        all_entities.update(turn.entities)
    all_entities.update(query.entities)  # Current takes precedence

    params["entities"] = all_entities
    return params
```

---

## Success Checklist

Before proceeding to Lab 06, ensure all items are checked:

- [ ] QueryAgent parses messages into StructuredQuery with intent and entities
- [ ] Intent classification confidence score is included
- [ ] RouterAgent routes to correct ActionAgent based on intent
- [ ] Routing includes fallback agent for error handling
- [ ] At least 3 ActionAgents implemented and working
- [ ] RetrieveAgent uses hybrid search from Lab 04
- [ ] Pipeline connects all agents in correct order
- [ ] Error handling returns graceful responses
- [ ] Session ID generated and returned
- [ ] Conversation history maintained across turns
- [ ] Context influences subsequent responses
- [ ] Entities persist within session
- [ ] All pipeline tests pass
- [ ] All session tests pass

**Estimated Time:** 2-3 hours

**Points Possible:** 25 (Agent Orchestration)

**Prerequisites:**
- Lab 04 completed (RAG Pipeline with RetrieveAgent)
- Understanding of three-agent pattern (Lab 01)
- Azure OpenAI configured and accessible

**Next Step:** Proceed to Lab 06 - Deploy with azd

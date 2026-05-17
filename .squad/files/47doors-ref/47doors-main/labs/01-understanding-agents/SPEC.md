# Lab 01 - Understanding AI Agents: Completion Specification

## What "Done" Looks Like

Lab 01 is complete when you have built a working intent classifier and demonstrated understanding of multi-agent system design patterns. You should be able to:

1. Build an intent classifier that correctly routes user queries to appropriate handlers
2. Explain the three-agent pattern and when to use it
3. Complete both hands-on exercises with passing tests
4. Articulate the differences between single-agent and multi-agent architectures

A successfully completed Lab 01 means you understand the foundational concepts of AI agent design and can proceed to implementing more complex agent patterns in subsequent labs.

---

## Checkable Deliverables

### 1. Intent Classifier Achieves >90% Accuracy on Test Queries

**What it verifies:**
- Your classifier correctly categorizes user intents
- Edge cases and ambiguous queries are handled appropriately
- The classifier generalizes beyond training examples

**Acceptance Criteria:**
- [ ] Intent classifier implementation is complete in the designated file
- [ ] Classifier correctly identifies at least 5 distinct intent categories
- [ ] Test suite passes with >90% accuracy (minimum 9/10 test queries correct)
- [ ] Classifier handles unknown/out-of-scope intents gracefully
- [ ] Response time is under 500ms per classification (mock mode) or under 2000ms (Azure mode)

**How to Test:**
```bash
cd labs/01-understanding-agents
python -m pytest test_intent_classifier.py -v
```

**Expected Output:**
```
test_intent_classifier.py::test_greeting_intent PASSED
test_intent_classifier.py::test_help_intent PASSED
test_intent_classifier.py::test_ticket_intent PASSED
test_intent_classifier.py::test_knowledge_intent PASSED
test_intent_classifier.py::test_farewell_intent PASSED
test_intent_classifier.py::test_ambiguous_intent PASSED
test_intent_classifier.py::test_unknown_intent PASSED
test_intent_classifier.py::test_accuracy_threshold PASSED

========================= 8 passed in X.XXs =========================
```

**Accuracy Calculation:**
```python
# The accuracy test verifies:
correct_classifications = sum(1 for query, expected in test_cases
                              if classifier.classify(query) == expected)
accuracy = correct_classifications / len(test_cases)
assert accuracy >= 0.90, f"Accuracy {accuracy:.1%} is below 90% threshold"
```

---

### 2. Can Explain the Three-Agent Pattern

**What it verifies:**
- Understanding of the Router-Specialist-Orchestrator pattern
- Knowledge of when and why to use multi-agent architectures
- Ability to identify agent responsibilities and boundaries

**Acceptance Criteria:**
- [ ] Can name and describe the three agent types (Router, Specialist, Orchestrator)
- [ ] Can explain the responsibility of each agent type:
  - **Router Agent:** Classifies intent, routes to appropriate specialist
  - **Specialist Agent:** Deep domain expertise, handles specific task types
  - **Orchestrator Agent:** Coordinates multi-step workflows, manages state
- [ ] Can describe at least 2 benefits of multi-agent over single-agent design
- [ ] Can identify a scenario where single-agent design is preferable
- [ ] Written explanation is included in `exercises/three_agent_explanation.md`

**Assessment Questions (answer in explanation file):**

1. **What is the primary responsibility of a Router Agent?**
   - Expected: Analyze incoming requests, classify intent, direct to appropriate specialist

2. **When would you choose a Specialist Agent over a general-purpose agent?**
   - Expected: When domain expertise matters, when task requires specific tools/knowledge, when response quality must be high in a specific area

3. **What state does an Orchestrator Agent typically manage?**
   - Expected: Conversation context, multi-step workflow progress, agent coordination, error recovery

4. **Name two benefits of the three-agent pattern:**
   - Expected: Separation of concerns, easier testing, scalability, maintainability, specialization

**How to Verify:**
```bash
# Check that explanation file exists and has content
cat exercises/three_agent_explanation.md

# File should be at least 200 words
wc -w exercises/three_agent_explanation.md
```

---

### 3. Completed Both Exercises

**What it verifies:**
- Hands-on implementation of agent concepts
- Understanding through practical application

#### Exercise 1: Build the Intent Classifier

**Description:** Implement an intent classification system that can route user queries to appropriate handlers.

**Acceptance Criteria:**
- [ ] `intent_classifier.py` contains a working `IntentClassifier` class
- [ ] Classifier implements the required interface: `classify(query: str) -> Intent`
- [ ] At least 5 intent categories are supported (e.g., GREETING, HELP, TICKET, KNOWLEDGE, FAREWELL)
- [ ] Includes confidence scoring for each classification
- [ ] Handles edge cases (empty input, very long input, special characters)
- [ ] All unit tests pass

**Required File Structure:**
```
labs/01-understanding-agents/
  exercises/
    intent_classifier.py      # Your implementation
    test_intent_classifier.py # Test suite (provided)
```

**Interface Contract:**
```python
from enum import Enum
from dataclasses import dataclass

class Intent(Enum):
    GREETING = "greeting"
    HELP = "help"
    TICKET = "ticket"
    KNOWLEDGE = "knowledge"
    FAREWELL = "farewell"
    UNKNOWN = "unknown"

@dataclass
class ClassificationResult:
    intent: Intent
    confidence: float  # 0.0 to 1.0
    raw_query: str

class IntentClassifier:
    def classify(self, query: str) -> ClassificationResult:
        """Classify the intent of a user query."""
        ...
```

---

#### Exercise 2: Design a Multi-Agent System

**Description:** Design (on paper/markdown) a multi-agent system for a specific use case.

**Acceptance Criteria:**
- [ ] `exercises/multi_agent_design.md` contains your system design
- [ ] Design includes at least 3 agents with clearly defined roles
- [ ] Agent communication patterns are specified (sync/async, message format)
- [ ] Error handling strategy is documented
- [ ] Diagram or visual representation is included (ASCII or image)
- [ ] Design addresses the provided use case scenario

**Design Document Requirements:**

1. **Agent Definitions:**
   - Name and purpose of each agent
   - Input/output specifications
   - Tools or capabilities each agent has access to

2. **Communication Flow:**
   - How agents pass information
   - Message format/schema
   - Synchronous vs asynchronous patterns

3. **Error Handling:**
   - What happens when an agent fails
   - Retry strategies
   - Fallback behaviors

4. **Diagram:**
   - Visual representation of agent interactions
   - Data flow arrows
   - External system integrations

**Example ASCII Diagram:**
```
                     +-------------+
                     |   Router    |
                     |   Agent     |
                     +------+------+
                            |
          +-----------------+-----------------+
          |                 |                 |
    +-----v-----+     +-----v-----+     +-----v-----+
    | Specialist|     | Specialist|     | Specialist|
    |  (Tickets)|     | (Knowledge)|    |   (FAQ)   |
    +-----------+     +-----------+     +-----------+
```

---

## Assessment Rubric

### Total Points: 15 (Intent Classification Focus)

| Criteria | Points | Description |
|----------|--------|-------------|
| **Intent Classification Accuracy** | 6 | Classifier achieves >90% accuracy on test suite |
| **Code Quality** | 3 | Clean, well-documented code with proper error handling |
| **Intent Categories** | 2 | Supports 5+ meaningful intent categories |
| **Confidence Scoring** | 2 | Accurate confidence scores that correlate with actual correctness |
| **Edge Case Handling** | 2 | Gracefully handles malformed, empty, or unusual input |

### Detailed Scoring Guide

#### Intent Classification Accuracy (6 points)
- **6 points:** >95% accuracy, handles all test cases including edge cases
- **5 points:** 90-95% accuracy, minor issues with ambiguous cases
- **4 points:** 85-90% accuracy, consistent issues with specific intents
- **3 points:** 80-85% accuracy, multiple categories confused
- **2 points:** 70-80% accuracy, fundamental classification issues
- **0-1 points:** <70% accuracy, classifier not functional

#### Code Quality (3 points)
- **3 points:** Clean code, comprehensive docstrings, type hints, follows PEP 8
- **2 points:** Readable code, basic documentation, mostly follows conventions
- **1 point:** Functional but messy, limited documentation
- **0 points:** Hard to read, no documentation, poor structure

#### Intent Categories (2 points)
- **2 points:** 5+ well-defined, non-overlapping categories with clear boundaries
- **1 point:** 5 categories but with significant overlap or unclear definitions
- **0 points:** Fewer than 5 categories or poorly defined

#### Confidence Scoring (2 points)
- **2 points:** Confidence scores accurately predict classification correctness
- **1 point:** Confidence scores provided but don't correlate well with accuracy
- **0 points:** No confidence scoring or always returns same confidence

#### Edge Case Handling (2 points)
- **2 points:** All edge cases handled gracefully (empty, long, special chars, multilingual)
- **1 point:** Most common edge cases handled
- **0 points:** Edge cases cause errors or incorrect behavior

---

## Common Failure Modes and Resolutions

### Low Classification Accuracy

**Symptom:** Test suite reports <90% accuracy

**Resolution:**
1. Review misclassified queries - look for patterns
2. Expand training examples for weak categories
3. Add keyword detection for clear-cut cases
4. Consider using embeddings for semantic similarity
5. Check for overlapping intent definitions

```python
# Debug misclassifications
for query, expected in test_cases:
    result = classifier.classify(query)
    if result.intent != expected:
        print(f"MISS: '{query}' -> {result.intent} (expected {expected})")
```

---

### Intent Categories Too Broad/Narrow

**Symptom:** Many queries fall into UNKNOWN or single dominant category

**Resolution:**
1. Analyze query distribution in test set
2. Split broad categories into specific sub-intents
3. Merge categories that are rarely distinguishable
4. Add more training examples for minority categories

---

### Confidence Scores Not Meaningful

**Symptom:** All queries return similar confidence regardless of clarity

**Resolution:**
1. Use probability distributions from model outputs
2. Calculate distance to decision boundary
3. Compare top-2 scores (high confidence = large gap)
4. Calibrate scores using validation set

```python
def calculate_confidence(scores: dict) -> float:
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) >= 2:
        # Confidence based on margin between top choices
        return sorted_scores[0] - sorted_scores[1]
    return sorted_scores[0]
```

---

### Edge Case Crashes

**Symptom:** Classifier throws exceptions on unusual input

**Resolution:**
```python
def classify(self, query: str) -> ClassificationResult:
    # Input validation
    if not query or not isinstance(query, str):
        return ClassificationResult(Intent.UNKNOWN, 0.0, str(query))

    # Normalize input
    query = query.strip()[:MAX_QUERY_LENGTH]

    if not query:
        return ClassificationResult(Intent.UNKNOWN, 0.0, query)

    # Proceed with classification...
```

---

### Test File Not Found

**Symptom:** `ModuleNotFoundError` when running tests

**Resolution:**
```bash
# Ensure you're in the correct directory
cd labs/01-understanding-agents

# Verify file structure
ls -la exercises/

# Run tests with correct path
python -m pytest exercises/test_intent_classifier.py -v
```

---

## Success Checklist

Before proceeding to Lab 02, ensure all items are checked:

- [ ] `intent_classifier.py` is implemented and follows the required interface
- [ ] All unit tests pass with >90% accuracy
- [ ] `three_agent_explanation.md` is complete (200+ words)
- [ ] `multi_agent_design.md` contains system design with diagram
- [ ] Can verbally explain the Router-Specialist-Orchestrator pattern
- [ ] Code is clean, documented, and handles edge cases

**Estimated Time:** 2-3 hours

**Points Possible:** 15 (Intent Classification)

**Next Step:** Proceed to Lab 02 - Building Conversational Agents

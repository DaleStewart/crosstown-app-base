# 🤖 Lab 01 - Understanding AI Agents

| 📋 Attribute | Value |
|-------------|-------|
| ⏱️ **Duration** | 90 minutes |
| 📊 **Difficulty** | ⭐⭐ Intermediate |
| 🎯 **Prerequisites** | Lab 00 completed |

---

## 📈 Progress Tracker

```
Lab Progress: [░░░░░░░░░░] 0% - Not Started

Checkpoints:
□ Understand Multi-Agent Architecture
□ Learn QueryAgent Pattern
□ Learn RouterAgent Pattern
□ Learn ActionAgent Pattern
□ Complete Exercise 1a: Intent Classification
□ Complete Exercise 1b: Prompt Engineering
□ Achieve >90% Intent Accuracy
□ Complete Self-Assessment
```

---

## 🎯 Learning Objectives

By the end of this lab, you will be able to:

1. 🏗️ **Understand multi-agent vs single agent architectures** - Compare the trade-offs between monolithic AI systems and distributed agent patterns
2. 🔄 **Learn the QueryAgent → RouterAgent → ActionAgent pattern** - Master the three-agent architecture used throughout this accelerator
3. 🎯 **Practice intent classification** - Build and test an intent classifier that routes user queries to the appropriate agent

---

## 🤔 Why Multi-Agent Over Monolithic?

When building AI-powered applications, a natural first instinct is to create a single, powerful agent that handles everything. While this works for simple use cases, it quickly becomes problematic as complexity grows.

### ❌ The Monolithic Problem

A single-agent architecture suffers from:

| 🚫 Issue | 📝 Description |
|---------|-------------|
| **Prompt Bloat** | System prompts grow unwieldy as you add more capabilities |
| **Context Confusion** | The model struggles to stay focused when handling disparate tasks |
| **Testing Difficulty** | Hard to isolate and test specific behaviors |
| **Maintenance Burden** | Changes to one capability risk breaking others |
| **Cost Inefficiency** | Every request pays for the full prompt, even for simple tasks |

### ✅ The Multi-Agent Solution

Breaking your system into specialized agents provides:

- 🎯 **Separation of Concerns** - Each agent has a clear, bounded responsibility
- 📝 **Focused Prompts** - Shorter, more precise instructions lead to better outputs
- 🧪 **Independent Testing** - Test each agent in isolation
- 📈 **Selective Scaling** - Route simple queries to cheaper/faster models
- 🔍 **Easier Debugging** - Trace issues to specific agents in the pipeline

---

## 🔄 The Three-Agent Pattern

This accelerator uses a proven three-agent architecture that balances simplicity with power:

```
                                    +------------------+
                                    |   ActionAgent    |
                                    |   (RAG Search)   |
                                    +------------------+
                                           ^
                                           |
+------------------+    +------------------+
|   QueryAgent     |--->|   RouterAgent    |
| (Understanding)  |    |  (Dispatching)   |
+------------------+    +------------------+
        ^                      |
        |                      v
   User Query           +------------------+
                        |   ActionAgent    |
                        |   (API Call)     |
                        +------------------+
                               |
                               v
                        +------------------+
                        |   ActionAgent    |
                        | (Conversation)   |
                        +------------------+
```

### 👥 Agent Responsibilities

#### 🔍 QueryAgent - The Understander

**Purpose:** Transform raw user input into structured, actionable data.

**Responsibilities:**
- 📝 Parse natural language queries
- 🏷️ Extract entities (names, dates, amounts, etc.)
- ✨ Normalize input (fix typos, expand abbreviations)
- 🎯 Identify query type and intent
- 📚 Enrich context with conversation history

| 📥 Input | 📤 Output |
|----------|----------|
| Raw user message + conversation context | Structured query object with intent, entities, and metadata |

#### 🚦 RouterAgent - The Dispatcher

**Purpose:** Determine the best action path for a given query.

**Responsibilities:**
- 🏷️ Classify intent into predefined categories
- ✅ Select appropriate ActionAgent(s)
- ❓ Handle ambiguous queries (ask for clarification)
- 📋 Apply business rules and access control
- 📊 Log routing decisions for analytics

| 📥 Input | 📤 Output |
|----------|----------|
| Structured query from QueryAgent | Routing decision with selected agent(s) and parameters |

#### ⚡ ActionAgent(s) - The Doers

**Purpose:** Execute specific tasks and generate responses.

**Types of ActionAgents:**
- 📚 **RAG Agent** - Searches knowledge bases and synthesizes answers
- 🔗 **API Agent** - Calls external services and transforms responses
- 💬 **Conversation Agent** - Handles chitchat and clarifications
- 📋 **Task Agent** - Performs multi-step workflows

| 📥 Input | 📤 Output |
|----------|----------|
| Routing decision with parameters | Final response to user |

---

## 🛡️ Agent Boundaries and Responsibilities

Clear boundaries between agents are critical. Here is a decision matrix:

| 📋 Concern | 🔍 QueryAgent | 🚦 RouterAgent | ⚡ ActionAgent |
|---------|------------|-------------|-------------|
| Parse user input | ✅ Yes | ❌ No | ❌ No |
| Classify intent | 🔶 Partial | ✅ Yes | ❌ No |
| Select execution path | ❌ No | ✅ Yes | ❌ No |
| Call external APIs | ❌ No | ❌ No | ✅ Yes |
| Generate final response | ❌ No | ❌ No | ✅ Yes |
| Maintain conversation state | ✅ Yes | ❌ No | 🔶 Partial |

### 🚫 Anti-Patterns to Avoid

1. ❌ **Router doing understanding** - Keep parsing in QueryAgent
2. ❌ **ActionAgent re-classifying** - Trust the router's decision
3. ❌ **QueryAgent calling APIs** - It should only understand, not act
4. ❌ **Circular dependencies** - Agents should not call back to earlier stages

---

## 📝 Exercises

Complete the following hands-on exercises to reinforce your understanding:

### 📚 Exercise 1a: Intent Classification
**File:** [exercises/01a-intent-classification.md](exercises/01a-intent-classification.md)

Build an intent classifier that categorizes user queries into predefined intents. You will:
- 🏷️ Define intent categories for your domain
- 📝 Create training examples for each intent
- 💻 Implement classification logic
- 🧪 Test against edge cases

### ✏️ Exercise 1b: Prompt Engineering
**File:** [exercises/01b-prompt-engineering.md](exercises/01b-prompt-engineering.md)

Craft effective prompts for each agent in the pipeline. You will:
- 🔍 Write a QueryAgent system prompt
- 🚦 Design a RouterAgent decision prompt
- ⚡ Create ActionAgent task prompts
- 🔄 Test prompt variations

---

## ✅ Deliverables

By the end of this lab, you should have:

| 📋 Deliverable | ✅ Success Criteria |
|-------------|------------------|
| 🎯 Intent Classifier | >90% accuracy on test queries |
| 📝 Agent Prompts | Three working prompts (Query, Router, Action) |
| 🏗️ Architecture Diagram | Your own version showing data flow |
| 🧪 Test Suite | At least 20 test queries with expected classifications |

---

## 🔧 Troubleshooting Tips

### ⚠️ Common Issues

**Issue:** Intent classifier accuracy below 90%
- ✅ **Solution:** Review misclassified examples and add them to training data
- ✅ **Solution:** Check for overlapping intent definitions - make categories more distinct
- ✅ **Solution:** Add more diverse examples per intent (aim for 10+ each)

**Issue:** RouterAgent selecting wrong ActionAgent
- ✅ **Solution:** Verify QueryAgent is extracting correct intent
- ✅ **Solution:** Review routing rules for gaps or conflicts
- ✅ **Solution:** Add explicit handling for edge cases

**Issue:** Prompts generating inconsistent outputs
- ✅ **Solution:** Add output format examples to your prompts
- ✅ **Solution:** Use structured output (JSON) where possible
- ✅ **Solution:** Lower temperature for more deterministic results

**Issue:** Context getting lost between agents
- ✅ **Solution:** Ensure conversation history is passed through pipeline
- ✅ **Solution:** Check that entity extraction preserves all relevant data
- ✅ **Solution:** Add logging to trace data flow between agents

### 📋 Debugging Checklist

1. [ ] ✅ Verify Lab 00 setup is complete and working
2. [ ] 🔑 Check that all API keys/endpoints are configured
3. [ ] 📝 Enable verbose logging for each agent
4. [ ] 🧪 Test each agent in isolation before testing the pipeline
5. [ ] 🔍 Compare actual vs expected outputs at each stage
6. [ ] ⚠️ Review Azure OpenAI rate limits if seeing throttling

### 🆘 Getting Help

- 📖 Review the architecture diagram above
- 📄 Check the exercise files for hints
- 📚 Consult the main accelerator documentation
- 👋 Reach out to your instructor or lab assistant

---

## 🧠 Check Your Understanding

Before proceeding to Lab 02, verify you can answer these questions:

### 📝 Concept Check

| ❓ Question | 📝 Your Answer |
|----------|-------------|
| Why is a multi-agent architecture better than a monolithic agent for complex systems? | _[Write your answer]_ |
| What is the primary responsibility of the QueryAgent? | _[Write your answer]_ |
| When should the RouterAgent escalate to a human instead of dispatching to an ActionAgent? | _[Write your answer]_ |
| What's the difference between a RAG ActionAgent and an API ActionAgent? | _[Write your answer]_ |

### ✅ Self-Assessment Checklist

Complete this checklist to confirm you're ready for Lab 02:

- [ ] 🗣️ I can explain the three-agent pattern to someone new
- [ ] 🎯 My intent classifier achieves >90% accuracy on test queries
- [ ] ✏️ I have written prompts for QueryAgent, RouterAgent, and ActionAgent
- [ ] 🔄 I understand why agents should NOT call back to earlier stages in the pipeline
- [ ] 🎨 I can draw an architecture diagram showing data flow between agents
- [ ] 🧪 I have at least 20 test queries with expected classifications

### 🧪 Quick Quiz

Test yourself with these scenarios:

1. **Scenario:** A user asks "What's my financial aid status?" and also mentions "my password isn't working"
   - 🔍 Which agent handles parsing both issues?
   - 🚦 How should the RouterAgent handle multiple intents?

2. **Scenario:** The QueryAgent extracts an intent but with only 60% confidence
   - ❓ Should the RouterAgent proceed or ask for clarification?
   - 📊 What factors influence this decision?

3. **Scenario:** An ActionAgent needs information that wasn't in the original query
   - 🔄 Can it call back to QueryAgent to re-parse?
   - ✅ What's the correct pattern to handle this?

**Answers:** Discuss with your coach or check [coach-guide/TALKING_POINTS.md](../../coach-guide/TALKING_POINTS.md) for guidance.

---

## ➡️ Next Steps

Once you have completed this lab and achieved >90% accuracy on your intent classifier, proceed to:

**[Lab 02 - Azure MCP Setup](../02-azure-mcp-setup/README.md)** ☁️

In the next lab, you will configure Azure OpenAI and Azure AI Search services to power your agents.

---

## 📊 Version Matrix

| Component | Required Version | Tested Version |
|-----------|-----------------|----------------|
| 🐍 Python | 3.11+ | 3.12.10 |
| 🤖 Azure OpenAI | GPT-4o | 2025-01-01-preview |
| 🔧 Pydantic | 2.5+ | 2.6.1 |
| 📝 Prompt Engineering | N/A | Best practices |

---

<div align="center">

[← Lab 00](../00-setup/README.md) | **Lab 01** | [Lab 02 →](../02-azure-mcp-setup/README.md)

📅 Last Updated: 2026-02-04 | 📝 Version: 1.0.0

</div>

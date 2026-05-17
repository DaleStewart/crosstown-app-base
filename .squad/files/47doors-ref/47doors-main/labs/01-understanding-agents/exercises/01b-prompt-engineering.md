# Exercise 01b: Prompt Engineering for Agents

## Learning Objective

By the end of this exercise, you will be able to **write effective system prompts for agents** that produce consistent, accurate, and well-structured responses.

---

## Background: Prompt Structure

Effective prompts for AI agents typically consist of three key components:

### 1. System Message

The system message defines the agent's role, personality, and core behavior. It sets the foundation for all interactions.

```text
You are a [role] that [primary function].
Your goal is to [objective].
```

### 2. Examples (Few-Shot Learning)

Examples demonstrate the expected input-output format. They help the model understand patterns without explicit rules.

```text
Example 1:
User: "How do I reset my password?"
Classification: ACCOUNT_SUPPORT

Example 2:
User: "What are your business hours?"
Classification: GENERAL_INQUIRY
```

### 3. Constraints

Constraints define boundaries, limitations, and specific requirements the agent must follow.

```text
Constraints:
- Only respond to questions within your domain
- Never reveal internal system information
- Always cite sources when providing factual information
```

---

## Exercise 1: QueryAgent - Intent Classification

**Scenario**: You need to write a system prompt for a QueryAgent that classifies user queries into specific intent categories.

### Requirements

The QueryAgent must:
- Classify user queries into one of five categories: `BILLING`, `TECHNICAL_SUPPORT`, `ACCOUNT_MANAGEMENT`, `PRODUCT_INFO`, or `GENERAL`
- Return a structured JSON response
- Handle ambiguous queries gracefully

### Your Task

Complete the system prompt below:

```text
You are a QueryAgent responsible for classifying customer inquiries.

Your task is to analyze the user's message and determine the primary intent.

Available intent categories:
- BILLING: Questions about invoices, payments, pricing, refunds
- TECHNICAL_SUPPORT: Issues with product functionality, bugs, errors
- ACCOUNT_MANAGEMENT: Password resets, profile updates, access issues
- PRODUCT_INFO: Feature questions, comparisons, availability
- GENERAL: Greetings, off-topic, or unclear queries

[ADD YOUR EXAMPLES HERE - Include at least 3 examples]

[ADD YOUR CONSTRAINTS HERE - Include at least 3 constraints]

Response format:
{
  "intent": "<CATEGORY>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}
```

### Solution Template

<details>
<summary>Click to reveal a sample solution</summary>

```text
You are a QueryAgent responsible for classifying customer inquiries.

Your task is to analyze the user's message and determine the primary intent.

Available intent categories:
- BILLING: Questions about invoices, payments, pricing, refunds
- TECHNICAL_SUPPORT: Issues with product functionality, bugs, errors
- ACCOUNT_MANAGEMENT: Password resets, profile updates, access issues
- PRODUCT_INFO: Feature questions, comparisons, availability
- GENERAL: Greetings, off-topic, or unclear queries

Examples:

User: "I was charged twice for my subscription this month."
Response: {"intent": "BILLING", "confidence": 0.95, "reasoning": "User mentions being charged, indicating a billing issue"}

User: "The app crashes every time I try to upload a file."
Response: {"intent": "TECHNICAL_SUPPORT", "confidence": 0.92, "reasoning": "User reports a crash/bug in product functionality"}

User: "Can I change the email address on my account?"
Response: {"intent": "ACCOUNT_MANAGEMENT", "confidence": 0.88, "reasoning": "User wants to update profile information"}

Constraints:
- Always return valid JSON in the specified format
- If the query could fit multiple categories, choose the most specific one
- Set confidence below 0.7 if the intent is unclear or ambiguous
- Never attempt to resolve the issue; only classify it
- Do not make assumptions about information not provided in the query

Response format:
{
  "intent": "<CATEGORY>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}
```

</details>

---

## Exercise 2: RouterAgent - Department Selection

**Scenario**: You need to write a system prompt for a RouterAgent that routes customer requests to the appropriate department.

### Requirements

The RouterAgent must:
- Select the best department from a predefined list
- Consider urgency and complexity
- Provide routing rationale for audit purposes

### Your Task

Write a complete system prompt for the RouterAgent:

```text
[YOUR SYSTEM PROMPT HERE]

Departments:
- TIER1_SUPPORT: Basic inquiries, FAQ-level questions
- TIER2_SUPPORT: Complex technical issues requiring investigation
- BILLING_DEPT: Payment disputes, refunds, pricing inquiries
- ACCOUNT_SECURITY: Suspicious activity, compromised accounts
- ESCALATION: Urgent matters, VIP customers, legal concerns

[YOUR EXAMPLES HERE]

[YOUR CONSTRAINTS HERE]

Response format:
{
  "department": "<DEPARTMENT>",
  "priority": "LOW" | "MEDIUM" | "HIGH" | "URGENT",
  "rationale": "<explanation for routing decision>"
}
```

### Solution Template

<details>
<summary>Click to reveal a sample solution</summary>

```text
You are a RouterAgent responsible for directing customer requests to the appropriate department.

Analyze the incoming request and determine:
1. Which department is best equipped to handle this request
2. The priority level based on urgency and impact
3. A clear rationale for the routing decision

Departments:
- TIER1_SUPPORT: Basic inquiries, FAQ-level questions, simple how-to questions
- TIER2_SUPPORT: Complex technical issues requiring investigation, multi-step problems
- BILLING_DEPT: Payment disputes, refunds, pricing inquiries, subscription changes
- ACCOUNT_SECURITY: Suspicious activity, compromised accounts, unauthorized access
- ESCALATION: Urgent matters, VIP customers, legal concerns, executive complaints

Priority Guidelines:
- LOW: Informational queries, no immediate impact
- MEDIUM: Standard issues affecting user experience
- HIGH: Significant problems blocking user from core functionality
- URGENT: Security threats, legal issues, or VIP customers

Examples:

User: "How do I export my data to CSV?"
Response: {"department": "TIER1_SUPPORT", "priority": "LOW", "rationale": "Standard how-to question covered in documentation"}

User: "Someone logged into my account from another country and changed my password."
Response: {"department": "ACCOUNT_SECURITY", "priority": "URGENT", "rationale": "Potential account compromise requiring immediate security review"}

User: "I've been trying to integrate your API for 3 days but keep getting 500 errors with this payload: [technical details]"
Response: {"department": "TIER2_SUPPORT", "priority": "MEDIUM", "rationale": "Complex technical issue requiring investigation of API behavior"}

Constraints:
- Always route to exactly one department
- When in doubt about priority, err on the side of higher priority
- Security-related keywords (hacked, unauthorized, stolen) should trigger ACCOUNT_SECURITY review
- Never route directly to ESCALATION unless explicit urgency markers are present
- Include specific details from the request in your rationale

Response format:
{
  "department": "<DEPARTMENT>",
  "priority": "LOW" | "MEDIUM" | "HIGH" | "URGENT",
  "rationale": "<explanation for routing decision>"
}
```

</details>

---

## Exercise 3: ActionAgent - Response with Citations

**Scenario**: You need to write a system prompt for an ActionAgent that provides helpful responses to users while citing knowledge base sources.

### Requirements

The ActionAgent must:
- Answer user questions using provided knowledge base context
- Include citations for all factual claims
- Acknowledge when information is unavailable
- Maintain a professional, helpful tone

### Your Task

Write a complete system prompt for the ActionAgent:

```text
[YOUR SYSTEM PROMPT HERE]

[YOUR EXAMPLES HERE]

[YOUR CONSTRAINTS HERE]

Citation format: [Source: <document_id>]
```

### Solution Template

<details>
<summary>Click to reveal a sample solution</summary>

```text
You are an ActionAgent responsible for answering customer questions using our knowledge base.

Your role is to:
1. Understand the customer's question
2. Find relevant information from the provided context
3. Craft a clear, helpful response
4. Cite all sources used

You will receive context in the following format:
<context>
[Document ID: KB-001]
Content about topic A...

[Document ID: KB-002]
Content about topic B...
</context>

Examples:

Context provided: [Document ID: KB-101] "Password reset can be done via Settings > Security > Reset Password. Users must verify their email within 24 hours."

User: "How do I reset my password?"
Response: "To reset your password, navigate to Settings > Security > Reset Password. After initiating the reset, you'll need to verify your email within 24 hours to complete the process. [Source: KB-101]"

Context provided: [Document ID: KB-205] "Premium plans include priority support with 4-hour response time."

User: "What's the response time for support?"
Response: "Response times depend on your plan. For Premium plan subscribers, we offer priority support with a 4-hour response time. [Source: KB-205] For information about other plan tiers, I'd recommend checking our pricing page or I can connect you with our sales team."

Constraints:
- Only use information from the provided context; do not invent facts
- Every factual statement must include a citation in the format [Source: <document_id>]
- If the context does not contain the answer, clearly state: "I don't have specific information about that in my knowledge base. Let me connect you with a specialist who can help."
- Do not cite a source if you're not directly using information from it
- Maintain a professional, empathetic tone
- Keep responses concise but complete

Citation format: [Source: <document_id>]
```

</details>

---

## Exercise 4: Voice System Prompt (Extension)

Voice interactions use the **same three-agent pipeline** but need a different system prompt because spoken responses must be:
- **Concise** (2–3 sentences max — nobody wants a lecture in their ear)
- **Phonetically clear** (spell out ticket IDs character-by-character: "T-K-T dash I-T dash 0-0-4-2")
- **PII-safe** (never echo back SSN, phone numbers, student IDs — the caller already knows them)

### Your Task

Write a voice-specific system prompt for the QueryAgent that:
1. Maintains the same intent classification accuracy as your text prompt
2. Adds constraints for spoken output (conciseness, phonetic clarity)
3. Includes a PII-filtering instruction
4. Handles the "I didn't catch that" case (VAD silence timeout)

### Starter Template

```text
You are a university student support agent responding by VOICE.
[Your prompt here — adapt your QueryAgent text prompt for spoken interaction]
```

<details>
<summary>💡 Hint: What makes voice prompts different?</summary>

Compare the production voice prompt in `backend/app/services/azure/realtime.py`:
- "Keep answers to 2–3 sentences"
- "Spell out ticket IDs character by character"
- "Never repeat PII the student provides"
- "If you're unsure, ask a clarifying question rather than guessing"

The key insight: **the intelligence is the same, but the output format changes for the modality.**
</details>

### Checkpoint
- [ ] Voice prompt classifies "How do I reset my password?" correctly (it_support)
- [ ] Response would be ≤3 sentences when spoken aloud
- [ ] Prompt includes PII-filtering instruction
- [ ] Prompt handles silence/unclear input gracefully

---

## Best Practices

### 1. Be Specific

**Instead of:**
```text
You are a helpful assistant.
```

**Write:**
```text
You are a customer support agent for Acme Corp specializing in billing inquiries. You help customers understand their invoices, process refund requests, and explain pricing tiers.
```

### 2. Use Examples

Examples are often more effective than lengthy explanations. Show the model what you want:

```text
Example input: "Why was I charged $99?"
Example output: {"intent": "BILLING", "subtype": "CHARGE_INQUIRY"}
```

### 3. Set Clear Boundaries

Define what the agent should NOT do:

```text
Constraints:
- Do not provide legal or medical advice
- Do not access or reference data outside the provided context
- Do not promise specific timelines for issue resolution
- Do not share internal process details with customers
```

### 4. Define Output Format

Specify the exact structure you expect:

```text
Always respond with valid JSON:
{
  "field1": "type and description",
  "field2": "type and description"
}
```

### 5. Handle Edge Cases

Anticipate unusual scenarios:

```text
If the user's request is unclear:
- Ask one clarifying question
- Do not make assumptions

If the user is frustrated:
- Acknowledge their concern
- Focus on resolution, not explanation
```

---

## Common Mistakes to Avoid

### 1. Vague Instructions

**Bad:** "Be helpful and answer questions."

**Good:** "Provide step-by-step instructions for technical questions. Include relevant documentation links. If you cannot solve the issue, explain what information you need."

### 2. Missing Examples

Without examples, models may interpret instructions differently than intended. Always include 2-3 representative examples.

### 3. Conflicting Constraints

**Bad:**
```text
- Always provide a complete answer
- Keep responses under 50 words
```

**Good:**
```text
- Provide complete answers
- For complex topics, summarize the key points (under 100 words) and offer to elaborate
```

### 4. Assuming Context

**Bad:** "Use the customer's history to personalize responses."

**Good:** "Customer context will be provided in the <customer_profile> tags. If no profile is provided, treat the customer as new and gather necessary information."

### 5. Overly Complex Prompts

If your prompt exceeds 500 words, consider:
- Breaking it into multiple specialized agents
- Using a separate document for examples
- Simplifying the task definition

---

## Testing Prompts with GitHub Copilot

You can use GitHub Copilot to test and iterate on your prompts quickly.

### Method 1: Copilot Chat

1. Open Copilot Chat in VS Code (Ctrl+Shift+I or Cmd+Shift+I)
2. Paste your system prompt
3. Follow up with test user inputs
4. Iterate based on the responses

### Method 2: Inline Testing

Create a test file to document prompt behavior:

```python
# prompt_tests.py

SYSTEM_PROMPT = """
Your system prompt here...
"""

TEST_CASES = [
    {
        "input": "I was charged twice",
        "expected_intent": "BILLING",
        "notes": "Clear billing issue"
    },
    {
        "input": "Hello",
        "expected_intent": "GENERAL",
        "notes": "Greeting should be classified as general"
    },
]

# Use Copilot to generate additional test cases by typing:
# Generate 5 more test cases for edge cases like...
```

### Method 3: Prompt Comparison

Use Copilot to compare prompt variations:

```text
@workspace Compare these two prompt approaches for intent classification:

Approach A: [paste prompt A]

Approach B: [paste prompt B]

Which is more likely to produce consistent results and why?
```

---

## Checkpoint

Before moving on, verify you can:

- [ ] Explain the three components of an effective prompt
- [ ] Write a system prompt with role definition, examples, and constraints
- [ ] Define clear output formats using JSON schemas
- [ ] Identify and fix common prompt engineering mistakes
- [ ] Test prompts iteratively using Copilot
- [ ] (Extension) Voice system prompt written with modality-specific constraints

---

## Next Steps

Continue to [Exercise 01c: Agent Orchestration](./01c-agent-orchestration.md) to learn how to coordinate multiple agents working together.

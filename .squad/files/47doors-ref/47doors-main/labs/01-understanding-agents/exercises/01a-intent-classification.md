# Exercise 01a: Intent Classification

## Learning Objective

Understand how intent classification works as the foundation of AI-powered student service agents. By the end of this exercise, you will be able to:

- Explain the role of intent classification in routing student queries
- Build a simple classifier using GitHub Copilot
- Test your classifier against real-world sample queries
- Achieve >90% accuracy on the provided test set

## Background

Intent classification is the first step in any conversational AI system. Before an agent can help a student, it must understand *what kind of help* they need. This determines which backend system to query, which knowledge base to search, or which human specialist to escalate to.

## Intent Categories

Your classifier must categorize student queries into one of these 7 categories:

| Intent | Description | Example Triggers |
|--------|-------------|------------------|
| `financial_aid` | FAFSA, scholarships, grants, tuition assistance | "FAFSA", "scholarship", "grant", "financial aid", "tuition help" |
| `registration` | Course enrollment, transcripts, graduation requirements | "register", "enroll", "transcript", "graduation", "drop class" |
| `housing` | Dormitories, roommates, move-in/move-out | "dorm", "roommate", "housing", "move-in", "residence hall" |
| `it_support` | Password resets, email issues, Canvas/LMS problems | "password", "email", "Canvas", "login", "WiFi", "LMS" |
| `academic_advising` | Degree requirements, major/minor selection, course planning | "major", "minor", "degree", "advisor", "requirements", "prerequisite" |
| `student_accounts` | Bills, refunds, payment plans, account holds | "bill", "payment", "refund", "balance", "tuition due", "hold" |
| `general` | Catch-all for queries requiring human escalation | Ambiguous queries, multiple intents, complaints |

## Practice Queries

Before building your classifier, manually classify these 10 queries to build intuition:

### Easy (Clear Intent)

1. **"How do I reset my university email password?"**
   - Expected: `it_support`
   - Rationale: Direct mention of password and email

2. **"When is the FAFSA deadline for next semester?"**
   - Expected: `financial_aid`
   - Rationale: Explicit FAFSA reference

3. **"I need to request an official transcript for grad school applications."**
   - Expected: `registration`
   - Rationale: Transcript request is a registrar function

### Medium (Requires Context Understanding)

4. **"My roommate assignment hasn't shown up in the portal yet."**
   - Expected: `housing`
   - Rationale: Roommate context indicates housing, even without "dorm"

5. **"I can't figure out which classes I still need for my computer science degree."**
   - Expected: `academic_advising`
   - Rationale: Degree requirements question, not course registration

6. **"There's a hold on my account preventing me from registering."**
   - Expected: `student_accounts`
   - Rationale: Account holds are typically financial/bursar issues

### Hard (Ambiguous or Multi-Intent)

7. **"I submitted my housing deposit but it's not showing on my student account."**
   - Expected: `student_accounts`
   - Rationale: Primary issue is account/payment visibility, not housing itself

8. **"Do I need to take calculus before I can register for physics?"**
   - Expected: `academic_advising`
   - Rationale: Prerequisite questions are advising, not registration

9. **"I'm having trouble with the Canvas assignment submission and I think my professor made a grading error."**
   - Expected: `general`
   - Rationale: Two separate issues (IT + academic dispute) require escalation

10. **"Everything about this university is terrible and I want to talk to someone in charge."**
    - Expected: `general`
    - Rationale: Complaint without specific intent requires human escalation

## Instructions

### Step 1: Create Your Classifier

Using GitHub Copilot, create a Python function that classifies student queries. Start with this skeleton:

```python
# intent_classifier.py

from typing import Literal

IntentType = Literal[
    "financial_aid",
    "registration",
    "housing",
    "it_support",
    "academic_advising",
    "student_accounts",
    "general"
]

def classify_intent(query: str) -> IntentType:
    """
    Classify a student query into one of 7 intent categories.

    Args:
        query: The student's question or request

    Returns:
        The classified intent category
    """
    # Use Copilot to help you implement this!
    # Hint: Start with keyword matching, then consider more sophisticated approaches
    pass
```

### Step 2: Implement Your Logic

Work with Copilot to implement the classifier. Consider these approaches (in order of sophistication):

1. **Keyword Matching**: Simple but effective for clear-cut cases
2. **Weighted Keywords**: Some words are stronger indicators than others
3. **Rule-Based Logic**: Handle edge cases and ambiguous queries
4. **Confidence Scoring**: Return `general` when confidence is low

### Step 3: Test Against Sample Queries

Create a test file that loads `sample_queries.json` and evaluates your classifier:

```python
# test_classifier.py

import json
from intent_classifier import classify_intent

def test_classifier():
    with open("sample_queries.json", "r") as f:
        test_cases = json.load(f)

    correct = 0
    total = len(test_cases)

    for case in test_cases:
        query = case["query"]
        expected = case["expected_intent"]
        predicted = classify_intent(query)

        if predicted == expected:
            correct += 1
            print(f"[PASS] {query[:50]}...")
        else:
            print(f"[FAIL] {query[:50]}...")
            print(f"       Expected: {expected}, Got: {predicted}")

    accuracy = correct / total * 100
    print(f"\nAccuracy: {accuracy:.1f}% ({correct}/{total})")
    return accuracy >= 90.0

if __name__ == "__main__":
    success = test_classifier()
    exit(0 if success else 1)
```

### Step 4: Iterate and Improve

Review your failures and refine your classifier:

- Are there keywords you missed?
- Are some keywords too broad (causing false positives)?
- Should certain intents take priority over others?

## Success Criteria

Your exercise is complete when:

- [ ] Your `classify_intent()` function handles all 7 intent categories
- [ ] You achieve **>90% accuracy** on `sample_queries.json`
- [ ] Your code is clean and well-commented
- [ ] You can explain *why* each classification decision was made

## Reflection Questions

After completing the exercise, consider:

1. What types of queries were hardest to classify? Why?
2. How would you handle a query that seems to belong to multiple categories?
3. What are the limitations of keyword-based classification?
4. How might you improve this classifier using machine learning?

## Next Steps

Once you've completed this exercise, proceed to:

- **Exercise 01b**: Enhancing your classifier with Azure OpenAI embeddings
- **Exercise 01c**: Building a complete routing agent with fallback logic

---

## Appendix: Sample `sample_queries.json` Format

Your test file should follow this format:

```json
[
  {
    "query": "How do I apply for financial aid?",
    "expected_intent": "financial_aid"
  },
  {
    "query": "I forgot my Canvas password",
    "expected_intent": "it_support"
  }
]
```

Create at least 20 test cases covering all 7 intents with varying difficulty levels.

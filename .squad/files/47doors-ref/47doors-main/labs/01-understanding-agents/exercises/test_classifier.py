"""
Test harness for intent_classifier.py
Loads sample queries and evaluates classification accuracy.
"""

import json
from intent_classifier import classify_intent


def test_classifier():
    """
    Test the intent classifier against sample_queries.json

    Returns:
        bool: True if accuracy >= 90%, False otherwise
    """
    # Load test cases from the shared sample queries
    with open("../../../shared/sample_queries.json", "r") as f:
        data = json.load(f)
        test_cases = data["queries"]

    correct = 0
    total = len(test_cases)
    failures = []

    for case in test_cases:
        query = case["query"]
        expected = case["expected_intent"]
        predicted = classify_intent(query)

        if predicted == expected:
            correct += 1
            print(f"[PASS] {query[:50]}...")
        else:
            failures.append(
                {"query": query, "expected": expected, "predicted": predicted}
            )
            print(f"[FAIL] {query[:50]}...")
            print(f"       Expected: {expected}, Got: {predicted}")

    accuracy = correct / total * 100
    print(f"\n{'='*60}")
    print(f"Accuracy: {accuracy:.1f}% ({correct}/{total})")
    print(f"Goal: 90%+")

    if accuracy >= 90:
        print(f"✅ SUCCESS! Exceeded 90% accuracy target!")
    else:
        print(f"❌ Need {int(total * 0.9) - correct} more correct to reach 90%")

    print(f"{'='*60}\n")

    return accuracy >= 90.0


if __name__ == "__main__":
    success = test_classifier()
    exit(0 if success else 1)

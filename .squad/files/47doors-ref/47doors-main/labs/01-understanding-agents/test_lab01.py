#!/usr/bin/env python3
"""
Lab 01 - Understanding AI Agents: Verification Script

Tests intent classification accuracy, code quality, and completeness of exercises.
Run this script to verify Lab 01 is complete.

Usage:
    python test_lab01.py [--verbose]
"""

import io
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Test constants
REQUIRED_INTENTS = ["greeting", "help", "ticket", "knowledge", "farewell", "unknown"]
MIN_ACCURACY_THRESHOLD = 0.90
MIN_EXPLANATION_WORDS = 200

# Test cases: (query, expected_intent_keywords)
INTENT_TEST_CASES = [
    # Greetings
    ("Hello!", ["greeting"]),
    ("Hi there, how are you?", ["greeting"]),
    ("Good morning!", ["greeting"]),

    # Help requests
    ("I need help with my account", ["help"]),
    ("Can you assist me?", ["help"]),
    ("I'm having trouble", ["help"]),

    # Ticket-related
    ("What's the status of my ticket?", ["ticket"]),
    ("I want to submit a support ticket", ["ticket"]),
    ("Check ticket TKT-12345", ["ticket"]),

    # Knowledge queries
    ("How do I reset my password?", ["knowledge"]),
    ("What are the library hours?", ["knowledge"]),
    ("Where is the registrar office?", ["knowledge"]),

    # Farewells
    ("Goodbye!", ["farewell"]),
    ("Thanks, bye!", ["farewell"]),
    ("That's all, thank you", ["farewell"]),

    # Unknown/ambiguous
    ("asdfghjkl", ["unknown"]),
    ("", ["unknown"]),
    ("12345", ["unknown"]),
]


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    message: str
    points: float = 0.0
    max_points: float = 0.0


class TestRunner:
    """Runs Lab 01 verification tests."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.lab_dir = Path(__file__).parent
        self.exercises_dir = self.lab_dir / "exercises"

    def log(self, message: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"  {message}")

    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)
        icon = "\u2705" if result.passed else "\u274c"
        print(f"{icon} {result.name}")
        if result.message and (not result.passed or self.verbose):
            print(f"   {result.message}")

    def test_classifier_file_exists(self) -> TestResult:
        """Check if intent_classifier.py exists."""
        classifier_path = self.exercises_dir / "intent_classifier.py"
        if classifier_path.exists():
            return TestResult(
                name="Intent classifier file exists",
                passed=True,
                message=str(classifier_path),
                points=1.0,
                max_points=1.0
            )
        return TestResult(
            name="Intent classifier file exists",
            passed=False,
            message=f"Expected file at {classifier_path}",
            points=0.0,
            max_points=1.0
        )

    def test_classifier_imports(self) -> TestResult:
        """Check if classifier can be imported."""
        try:
            sys.path.insert(0, str(self.exercises_dir))
            from intent_classifier import IntentClassifier
            return TestResult(
                name="Intent classifier imports successfully",
                passed=True,
                message="IntentClassifier class found",
                points=1.0,
                max_points=1.0
            )
        except ImportError as e:
            return TestResult(
                name="Intent classifier imports successfully",
                passed=False,
                message=f"Import error: {e}",
                points=0.0,
                max_points=1.0
            )
        except Exception as e:
            return TestResult(
                name="Intent classifier imports successfully",
                passed=False,
                message=f"Error: {e}",
                points=0.0,
                max_points=1.0
            )

    def test_classifier_accuracy(self) -> TestResult:
        """Test intent classifier accuracy."""
        try:
            sys.path.insert(0, str(self.exercises_dir))
            from intent_classifier import IntentClassifier

            classifier = IntentClassifier()
            correct = 0
            total = len(INTENT_TEST_CASES)
            misclassified = []

            for query, expected_keywords in INTENT_TEST_CASES:
                try:
                    result = classifier.classify(query)
                    intent_value = str(result.intent.value).lower() if hasattr(result.intent, 'value') else str(result.intent).lower()

                    # Check if any expected keyword matches
                    matched = any(kw in intent_value for kw in expected_keywords)
                    if matched:
                        correct += 1
                    else:
                        misclassified.append(f"'{query[:30]}...' -> {intent_value} (expected: {expected_keywords})")
                except Exception as e:
                    misclassified.append(f"'{query[:30]}...' -> ERROR: {e}")

            accuracy = correct / total if total > 0 else 0
            passed = accuracy >= MIN_ACCURACY_THRESHOLD

            # Calculate points: 6 points max for accuracy
            if accuracy >= 0.95:
                points = 6.0
            elif accuracy >= 0.90:
                points = 5.0
            elif accuracy >= 0.85:
                points = 4.0
            elif accuracy >= 0.80:
                points = 3.0
            elif accuracy >= 0.70:
                points = 2.0
            else:
                points = 1.0 if accuracy >= 0.50 else 0.0

            message = f"Accuracy: {accuracy:.1%} ({correct}/{total})"
            if misclassified and self.verbose:
                message += f"\n   Misclassified:\n   " + "\n   ".join(misclassified[:5])

            return TestResult(
                name=f"Classifier accuracy >= {MIN_ACCURACY_THRESHOLD:.0%}",
                passed=passed,
                message=message,
                points=points,
                max_points=6.0
            )
        except ImportError:
            return TestResult(
                name=f"Classifier accuracy >= {MIN_ACCURACY_THRESHOLD:.0%}",
                passed=False,
                message="Could not import IntentClassifier",
                points=0.0,
                max_points=6.0
            )
        except Exception as e:
            return TestResult(
                name=f"Classifier accuracy >= {MIN_ACCURACY_THRESHOLD:.0%}",
                passed=False,
                message=f"Error during testing: {e}",
                points=0.0,
                max_points=6.0
            )

    def test_confidence_scoring(self) -> TestResult:
        """Test if classifier provides confidence scores."""
        try:
            sys.path.insert(0, str(self.exercises_dir))
            from intent_classifier import IntentClassifier

            classifier = IntentClassifier()
            result = classifier.classify("Hello, I need help")

            if not hasattr(result, 'confidence'):
                return TestResult(
                    name="Confidence scoring implemented",
                    passed=False,
                    message="Result missing 'confidence' attribute",
                    points=0.0,
                    max_points=2.0
                )

            confidence = result.confidence
            if not isinstance(confidence, (int, float)):
                return TestResult(
                    name="Confidence scoring implemented",
                    passed=False,
                    message=f"Confidence should be numeric, got {type(confidence)}",
                    points=0.0,
                    max_points=2.0
                )

            if not (0.0 <= confidence <= 1.0):
                return TestResult(
                    name="Confidence scoring implemented",
                    passed=False,
                    message=f"Confidence {confidence} not in range [0, 1]",
                    points=1.0,
                    max_points=2.0
                )

            return TestResult(
                name="Confidence scoring implemented",
                passed=True,
                message=f"Confidence score: {confidence:.2f}",
                points=2.0,
                max_points=2.0
            )
        except ImportError:
            return TestResult(
                name="Confidence scoring implemented",
                passed=False,
                message="Could not import IntentClassifier",
                points=0.0,
                max_points=2.0
            )
        except Exception as e:
            return TestResult(
                name="Confidence scoring implemented",
                passed=False,
                message=f"Error: {e}",
                points=0.0,
                max_points=2.0
            )

    def test_edge_cases(self) -> TestResult:
        """Test handling of edge cases."""
        try:
            sys.path.insert(0, str(self.exercises_dir))
            from intent_classifier import IntentClassifier

            classifier = IntentClassifier()
            edge_cases = [
                ("", "empty string"),
                ("   ", "whitespace only"),
                ("a" * 10000, "very long input"),
                ("Hello! 123 @#$%", "special characters"),
                (None, "None input"),
            ]

            handled = 0
            errors = []

            for test_input, description in edge_cases:
                try:
                    result = classifier.classify(test_input)
                    if result is not None and hasattr(result, 'intent'):
                        handled += 1
                    else:
                        errors.append(f"{description}: returned invalid result")
                except Exception as e:
                    errors.append(f"{description}: {type(e).__name__}")

            # Calculate points based on edge cases handled
            ratio = handled / len(edge_cases)
            if ratio >= 0.8:
                points = 2.0
            elif ratio >= 0.6:
                points = 1.0
            else:
                points = 0.0

            passed = ratio >= 0.8
            message = f"Handled {handled}/{len(edge_cases)} edge cases"
            if errors and self.verbose:
                message += f"\n   Errors: {', '.join(errors[:3])}"

            return TestResult(
                name="Edge cases handled gracefully",
                passed=passed,
                message=message,
                points=points,
                max_points=2.0
            )
        except ImportError:
            return TestResult(
                name="Edge cases handled gracefully",
                passed=False,
                message="Could not import IntentClassifier",
                points=0.0,
                max_points=2.0
            )
        except Exception as e:
            return TestResult(
                name="Edge cases handled gracefully",
                passed=False,
                message=f"Error: {e}",
                points=0.0,
                max_points=2.0
            )

    def test_three_agent_explanation(self) -> TestResult:
        """Check if three-agent explanation document exists and is complete."""
        explanation_path = self.exercises_dir / "three_agent_explanation.md"

        if not explanation_path.exists():
            return TestResult(
                name="Three-agent explanation document",
                passed=False,
                message=f"Expected file at {explanation_path}",
                points=0.0,
                max_points=2.0
            )

        content = explanation_path.read_text(encoding='utf-8')
        word_count = len(content.split())

        if word_count < MIN_EXPLANATION_WORDS:
            return TestResult(
                name="Three-agent explanation document",
                passed=False,
                message=f"Document has {word_count} words (minimum: {MIN_EXPLANATION_WORDS})",
                points=1.0,
                max_points=2.0
            )

        # Check for key concepts
        key_concepts = ["router", "specialist", "orchestrator"]
        found_concepts = [c for c in key_concepts if c.lower() in content.lower()]

        if len(found_concepts) < 2:
            return TestResult(
                name="Three-agent explanation document",
                passed=False,
                message=f"Document missing key concepts. Found: {found_concepts}",
                points=1.0,
                max_points=2.0
            )

        return TestResult(
            name="Three-agent explanation document",
            passed=True,
            message=f"{word_count} words, covers: {', '.join(found_concepts)}",
            points=2.0,
            max_points=2.0
        )

    def test_multi_agent_design(self) -> TestResult:
        """Check if multi-agent design document exists."""
        design_path = self.exercises_dir / "multi_agent_design.md"

        if not design_path.exists():
            return TestResult(
                name="Multi-agent design document",
                passed=False,
                message=f"Expected file at {design_path}",
                points=0.0,
                max_points=2.0
            )

        content = design_path.read_text(encoding='utf-8')
        word_count = len(content.split())

        # Check for diagram indicators
        has_diagram = any(indicator in content for indicator in [
            "```", "+-", "->", "|", "Agent", "──", "─"
        ])

        if word_count < 100:
            return TestResult(
                name="Multi-agent design document",
                passed=False,
                message=f"Document too short ({word_count} words)",
                points=1.0,
                max_points=2.0
            )

        if not has_diagram:
            return TestResult(
                name="Multi-agent design document",
                passed=True,
                message=f"{word_count} words (consider adding a diagram)",
                points=1.5,
                max_points=2.0
            )

        return TestResult(
            name="Multi-agent design document",
            passed=True,
            message=f"{word_count} words with diagram",
            points=2.0,
            max_points=2.0
        )

    def run_all_tests(self) -> tuple[float, float]:
        """Run all tests and return (points_earned, max_points)."""
        print("\n" + "=" * 60)
        print("Lab 01 - Understanding AI Agents: Verification")
        print("=" * 60 + "\n")

        # Run tests
        self.add_result(self.test_classifier_file_exists())
        self.add_result(self.test_classifier_imports())
        self.add_result(self.test_classifier_accuracy())
        self.add_result(self.test_confidence_scoring())
        self.add_result(self.test_edge_cases())
        self.add_result(self.test_three_agent_explanation())
        self.add_result(self.test_multi_agent_design())

        # Calculate totals
        points_earned = sum(r.points for r in self.results)
        max_points = sum(r.max_points for r in self.results)

        return points_earned, max_points

    def print_summary(self, points_earned: float, max_points: float):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        # Calculate rubric score (out of 15)
        rubric_score = min(15, (points_earned / max_points) * 15) if max_points > 0 else 0

        print(f"\nTests passed: {passed}/{total}")
        print(f"Points earned: {points_earned:.1f}/{max_points:.1f}")
        print(f"Rubric score: {rubric_score:.1f}/15")

        if rubric_score >= 12:
            print("\n\u2705 EXEMPLARY - Excellent work!")
        elif rubric_score >= 9:
            print("\n\u2705 PROFICIENT - Lab 01 complete!")
        elif rubric_score >= 6:
            print("\n\u26a0\ufe0f DEVELOPING - Some improvements needed")
        else:
            print("\n\u274c BEGINNING - Please review requirements")

        print("\n" + "=" * 60)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    runner = TestRunner(verbose=verbose)
    points_earned, max_points = runner.run_all_tests()
    runner.print_summary(points_earned, max_points)

    # Return exit code based on pass/fail
    rubric_score = (points_earned / max_points) * 15 if max_points > 0 else 0
    return 0 if rubric_score >= 9 else 1


if __name__ == "__main__":
    sys.exit(main())

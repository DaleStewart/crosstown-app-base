#!/usr/bin/env python3
"""
Lab 03 - Spec-Driven Development: Verification Script

Tests the completeness and quality of spec and constitution documents,
and verifies code generation from specifications.

Usage:
    python test_lab03.py [--verbose]
"""

import io
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    message: str
    points: float = 0.0
    max_points: float = 0.0


class SpecAnalyzer:
    """Analyzes specification documents for completeness."""

    # Required sections for a complete spec
    SPEC_SECTIONS = [
        ("feature name", ["feature", "name", "title"]),
        ("description", ["description", "overview", "summary"]),
        ("user stories", ["user stor", "as a", "i want"]),
        ("requirements", ["requirement", "functional", "must", "shall"]),
        ("success criteria", ["success", "criteria", "acceptance", "done"]),
    ]

    CONSTITUTION_SECTIONS = [
        ("principles", ["principle", "value", "guideline"]),
        ("boundaries", ["boundar", "limit", "scope"]),
        ("prohibited", ["prohibit", "never", "must not", "forbidden"]),
    ]

    @staticmethod
    def count_user_stories(content: str) -> int:
        """Count user stories in content."""
        # Match patterns like "As a [user], I want [goal]"
        patterns = [
            r"[Aa]s a[n]?\s+\w+.*[Ii] want",
            r"[Aa]s a[n]?\s+\w+.*[Ii] can",
            r"\*\*User Story",
            r"- As a",
            r"\d+\.\s*As a",
        ]
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, content))
        return max(count, content.lower().count("as a "))

    @staticmethod
    def count_requirements(content: str) -> int:
        """Count functional requirements in content."""
        patterns = [
            r"(?:shall|must|should|will)\s+\w+",
            r"(?:FR|REQ|R)\d+",
            r"- The system",
            r"\d+\.\s*The (?:system|agent|feature)",
        ]
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, content, re.IGNORECASE))
        return max(count // 2, content.lower().count("requirement"))

    @staticmethod
    def check_sections(content: str, sections: list) -> tuple[list, list]:
        """Check which sections are present."""
        content_lower = content.lower()
        found = []
        missing = []

        for section_name, keywords in sections:
            if any(kw in content_lower for kw in keywords):
                found.append(section_name)
            else:
                missing.append(section_name)

        return found, missing


class TestRunner:
    """Runs Lab 03 verification tests."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.lab_dir = Path(__file__).parent
        self.analyzer = SpecAnalyzer()

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

    def find_spec_file(self) -> Optional[Path]:
        """Find the participant's spec file."""
        candidates = [
            self.lab_dir / "your-spec.md",
            self.lab_dir / "spec.md",
            self.lab_dir / "my-spec.md",
            self.lab_dir / "escalation-spec.md",
            self.lab_dir / "exercises" / "your-spec.md",
            self.lab_dir / "exercises" / "spec.md",
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    def find_constitution_file(self) -> Optional[Path]:
        """Find the participant's constitution file."""
        candidates = [
            self.lab_dir / "your-constitution.md",
            self.lab_dir / "constitution.md",
            self.lab_dir / "my-constitution.md",
            self.lab_dir / "exercises" / "your-constitution.md",
            self.lab_dir / "exercises" / "constitution.md",
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    def find_generated_code(self) -> list[Path]:
        """Find generated code files."""
        generated_dir = self.lab_dir / "generated"
        code_files = []

        # Check generated directory
        if generated_dir.exists():
            code_files.extend(generated_dir.glob("*.py"))
            code_files.extend(generated_dir.glob("*.ts"))
            code_files.extend(generated_dir.glob("*.js"))

        # Also check exercises directory
        exercises_dir = self.lab_dir / "exercises"
        if exercises_dir.exists():
            for pattern in ["escalation*.py", "*detector*.py", "*agent*.py"]:
                code_files.extend(exercises_dir.glob(pattern))

        return list(set(code_files))

    def test_spec_exists(self) -> TestResult:
        """Check if spec file exists."""
        spec_path = self.find_spec_file()

        if spec_path is None:
            return TestResult(
                name="Specification file exists",
                passed=False,
                message="Create your-spec.md in the lab directory",
                points=0.0,
                max_points=1.0
            )

        word_count = len(spec_path.read_text(encoding='utf-8').split())

        if word_count < 100:
            return TestResult(
                name="Specification file exists",
                passed=False,
                message=f"Spec file too short ({word_count} words)",
                points=0.5,
                max_points=1.0
            )

        return TestResult(
            name="Specification file exists",
            passed=True,
            message=f"Found {spec_path.name} ({word_count} words)",
            points=1.0,
            max_points=1.0
        )

    def test_spec_has_sections(self) -> TestResult:
        """Check if spec has required sections."""
        spec_path = self.find_spec_file()

        if spec_path is None:
            return TestResult(
                name="Specification has required sections",
                passed=False,
                message="Spec file not found",
                points=0.0,
                max_points=2.0
            )

        content = spec_path.read_text(encoding='utf-8')
        found, missing = self.analyzer.check_sections(
            content, SpecAnalyzer.SPEC_SECTIONS
        )

        completion_ratio = len(found) / len(SpecAnalyzer.SPEC_SECTIONS)

        if completion_ratio >= 0.8:
            points = 2.0
        elif completion_ratio >= 0.6:
            points = 1.5
        elif completion_ratio >= 0.4:
            points = 1.0
        else:
            points = 0.5

        message = f"Found: {', '.join(found)}"
        if missing and self.verbose:
            message += f"\n   Missing: {', '.join(missing)}"

        return TestResult(
            name="Specification has required sections",
            passed=completion_ratio >= 0.6,
            message=message,
            points=points,
            max_points=2.0
        )

    def test_spec_user_stories(self) -> TestResult:
        """Check if spec has sufficient user stories."""
        spec_path = self.find_spec_file()

        if spec_path is None:
            return TestResult(
                name="Specification has user stories (3+ required)",
                passed=False,
                message="Spec file not found",
                points=0.0,
                max_points=1.5
            )

        content = spec_path.read_text(encoding='utf-8')
        story_count = self.analyzer.count_user_stories(content)

        if story_count >= 3:
            return TestResult(
                name="Specification has user stories (3+ required)",
                passed=True,
                message=f"Found {story_count} user stories",
                points=1.5,
                max_points=1.5
            )
        elif story_count >= 1:
            return TestResult(
                name="Specification has user stories (3+ required)",
                passed=False,
                message=f"Found {story_count} user stories (need at least 3)",
                points=0.5 * story_count,
                max_points=1.5
            )
        else:
            return TestResult(
                name="Specification has user stories (3+ required)",
                passed=False,
                message="No user stories found. Use 'As a [user], I want [goal]' format",
                points=0.0,
                max_points=1.5
            )

    def test_spec_requirements(self) -> TestResult:
        """Check if spec has sufficient functional requirements."""
        spec_path = self.find_spec_file()

        if spec_path is None:
            return TestResult(
                name="Specification has requirements (5+ required)",
                passed=False,
                message="Spec file not found",
                points=0.0,
                max_points=1.5
            )

        content = spec_path.read_text(encoding='utf-8')
        req_count = self.analyzer.count_requirements(content)

        if req_count >= 5:
            return TestResult(
                name="Specification has requirements (5+ required)",
                passed=True,
                message=f"Found {req_count} requirements",
                points=1.5,
                max_points=1.5
            )
        elif req_count >= 2:
            return TestResult(
                name="Specification has requirements (5+ required)",
                passed=False,
                message=f"Found {req_count} requirements (need at least 5)",
                points=0.3 * req_count,
                max_points=1.5
            )
        else:
            return TestResult(
                name="Specification has requirements (5+ required)",
                passed=False,
                message="Add functional requirements using 'shall', 'must', or numbered list",
                points=0.0,
                max_points=1.5
            )

    def test_constitution_exists(self) -> TestResult:
        """Check if constitution file exists."""
        const_path = self.find_constitution_file()

        if const_path is None:
            return TestResult(
                name="Constitution file exists",
                passed=False,
                message="Create your-constitution.md in the lab directory",
                points=0.0,
                max_points=1.0
            )

        word_count = len(const_path.read_text(encoding='utf-8').split())

        if word_count < 50:
            return TestResult(
                name="Constitution file exists",
                passed=False,
                message=f"Constitution too short ({word_count} words)",
                points=0.5,
                max_points=1.0
            )

        return TestResult(
            name="Constitution file exists",
            passed=True,
            message=f"Found {const_path.name} ({word_count} words)",
            points=1.0,
            max_points=1.0
        )

    def test_constitution_content(self) -> TestResult:
        """Check if constitution has required sections."""
        const_path = self.find_constitution_file()

        if const_path is None:
            return TestResult(
                name="Constitution has principles and boundaries",
                passed=False,
                message="Constitution file not found",
                points=0.0,
                max_points=2.0
            )

        content = const_path.read_text(encoding='utf-8')
        found, missing = self.analyzer.check_sections(
            content, SpecAnalyzer.CONSTITUTION_SECTIONS
        )

        # Check for FERPA and accessibility
        has_ferpa = "ferpa" in content.lower() or "privacy" in content.lower()
        has_accessibility = "accessib" in content.lower() or "a11y" in content.lower()

        points = len(found) * 0.5
        if has_ferpa:
            points += 0.25
        if has_accessibility:
            points += 0.25

        message = f"Found: {', '.join(found)}"
        extras = []
        if has_ferpa:
            extras.append("FERPA")
        if has_accessibility:
            extras.append("accessibility")
        if extras:
            message += f" + {', '.join(extras)}"

        return TestResult(
            name="Constitution has principles and boundaries",
            passed=len(found) >= 2,
            message=message,
            points=min(points, 2.0),
            max_points=2.0
        )

    def test_code_generated(self) -> TestResult:
        """Check if code was generated from spec."""
        code_files = self.find_generated_code()

        if not code_files:
            return TestResult(
                name="Code generated from specification",
                passed=False,
                message="Create generated/ directory with code files from Copilot",
                points=0.0,
                max_points=1.0
            )

        # Analyze generated code
        total_lines = 0
        for code_file in code_files:
            content = code_file.read_text(encoding='utf-8')
            total_lines += len(content.splitlines())

        files_list = ", ".join(f.name for f in code_files[:3])
        if len(code_files) > 3:
            files_list += f"... (+{len(code_files) - 3} more)"

        if total_lines < 20:
            return TestResult(
                name="Code generated from specification",
                passed=False,
                message=f"Code too minimal ({total_lines} lines). Generate more from spec.",
                points=0.5,
                max_points=1.0
            )

        return TestResult(
            name="Code generated from specification",
            passed=True,
            message=f"Found {len(code_files)} file(s): {files_list} ({total_lines} lines)",
            points=1.0,
            max_points=1.0
        )

    def test_validation_notes(self) -> TestResult:
        """Check if validation notes exist."""
        notes_locations = [
            self.lab_dir / "generated" / "validation_notes.md",
            self.lab_dir / "generated" / "notes.md",
            self.lab_dir / "validation_notes.md",
            self.lab_dir / "exercises" / "validation_notes.md",
        ]

        for notes_path in notes_locations:
            if notes_path.exists():
                content = notes_path.read_text(encoding='utf-8')
                word_count = len(content.split())

                if word_count >= 30:
                    return TestResult(
                        name="Validation notes documenting spec-to-code process",
                        passed=True,
                        message=f"Found {notes_path.name} ({word_count} words)",
                        points=0.5,
                        max_points=0.5
                    )

        return TestResult(
            name="Validation notes documenting spec-to-code process",
            passed=False,
            message="Create validation_notes.md describing how spec guided code generation",
            points=0.0,
            max_points=0.5
        )

    def run_all_tests(self) -> tuple[float, float]:
        """Run all tests and return (points_earned, max_points)."""
        print("\n" + "=" * 60)
        print("Lab 03 - Spec-Driven Development: Verification")
        print("=" * 60 + "\n")

        # Specification tests
        print("Specification Document:")
        self.add_result(self.test_spec_exists())
        self.add_result(self.test_spec_has_sections())
        self.add_result(self.test_spec_user_stories())
        self.add_result(self.test_spec_requirements())

        # Constitution tests
        print("\nConstitution Document:")
        self.add_result(self.test_constitution_exists())
        self.add_result(self.test_constitution_content())

        # Code generation tests
        print("\nCode Generation:")
        self.add_result(self.test_code_generated())
        self.add_result(self.test_validation_notes())

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

        # Calculate rubric score (out of 10)
        rubric_score = min(10, (points_earned / max_points) * 10) if max_points > 0 else 0

        print(f"\nTests passed: {passed}/{total}")
        print(f"Points earned: {points_earned:.1f}/{max_points:.1f}")
        print(f"Rubric score: {rubric_score:.1f}/10")

        if rubric_score >= 8:
            print("\n\u2705 EXEMPLARY - Excellent spec-driven development!")
        elif rubric_score >= 6:
            print("\n\u2705 PROFICIENT - Lab 03 complete!")
        elif rubric_score >= 4:
            print("\n\u26a0\ufe0f DEVELOPING - Documents need more detail")
        else:
            print("\n\u274c BEGINNING - Please complete spec and constitution")

        print("\n" + "=" * 60)
        print("\nExpected file structure:")
        print("  03-spec-driven-development/")
        print("    your-spec.md           # Feature specification")
        print("    your-constitution.md   # Agent constitution/guardrails")
        print("    generated/             # Code generated from spec")
        print("      escalation_detector.py")
        print("      validation_notes.md")
        print("=" * 60)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    runner = TestRunner(verbose=verbose)
    points_earned, max_points = runner.run_all_tests()
    runner.print_summary(points_earned, max_points)

    # Return exit code based on pass/fail
    rubric_score = (points_earned / max_points) * 10 if max_points > 0 else 0
    return 0 if rubric_score >= 6 else 1


if __name__ == "__main__":
    sys.exit(main())

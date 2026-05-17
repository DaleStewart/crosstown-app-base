#!/usr/bin/env python3
"""
Lab 07 - MCP Server (Stretch Goal): Verification Script

Tests MCP server implementation, tool definitions, and VS Code integration.
Run this script to verify Lab 07 is complete.

Usage:
    python test_lab07.py [--verbose]

Note: This is a STRETCH GOAL. Lab 07 is optional and not required for
boot camp certification. Completing this lab demonstrates advanced
understanding of MCP and agent integration.
"""

import ast
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def run_command(command: list[str], timeout: int = 30) -> tuple[bool, str, str]:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(sys.platform == "win32"),
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", "Command not found"
    except Exception as e:
        return False, "", str(e)


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    message: str
    points: float = 0.0
    max_points: float = 0.0


class MCPServerAnalyzer:
    """Analyzes MCP server implementation."""

    REQUIRED_TOOLS = [
        "university_support_query",
        "list_faq_categories",
        "get_category_faqs",
        "submit_support_ticket",
    ]

    @staticmethod
    def find_tools_in_code(content: str) -> list[str]:
        """Extract tool names from Python code."""
        tools = []

        # Look for tool definitions in various patterns
        patterns = [
            r'name\s*[=:]\s*["\'](\w+)["\']',
            r'@tool\s*\(\s*["\'](\w+)["\']',
            r'def\s+(\w+_tool)\s*\(',
            r'Tool\s*\(\s*name\s*=\s*["\'](\w+)["\']',
            r'["\']name["\']\s*:\s*["\'](\w+)["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            tools.extend(matches)

        # Also look for our specific required tools
        for tool in MCPServerAnalyzer.REQUIRED_TOOLS:
            if tool in content:
                tools.append(tool)

        return list(set(tools))

    @staticmethod
    def check_mcp_imports(content: str) -> list[str]:
        """Check for MCP-related imports."""
        mcp_patterns = [
            r"from\s+mcp",
            r"import\s+mcp",
            r"from\s+anthropic",
            r"import\s+anthropic",
            r"McpServer",
            r"mcp\.server",
            r"stdio_server",
        ]

        found = []
        for pattern in mcp_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(pattern.replace("\\s+", " ").replace(r"\.", "."))

        return found


class TestRunner:
    """Runs Lab 07 verification tests."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.lab_dir = Path(__file__).parent
        self.project_root = self.lab_dir.parent.parent
        self.analyzer = MCPServerAnalyzer()

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

    def find_mcp_server_file(self) -> Optional[Path]:
        """Find the MCP server implementation file."""
        candidates = [
            self.project_root / "backend" / "app" / "mcp_server.py",
            self.project_root / "backend" / "mcp_server.py",
            self.project_root / "backend" / "mcp_main.py",
            self.lab_dir / "solution" / "mcp_server.py",
            self.lab_dir / "mcp_server.py",
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    def find_mcp_main_file(self) -> Optional[Path]:
        """Find the MCP main entry point."""
        candidates = [
            self.project_root / "backend" / "mcp_main.py",
            self.project_root / "backend" / "app" / "mcp_main.py",
            self.project_root / "mcp_main.py",
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    def find_vscode_mcp_config(self) -> Optional[Path]:
        """Find VS Code MCP configuration."""
        candidates = [
            self.project_root / ".vscode" / "mcp.json",
            self.project_root / ".claude" / "settings.local.json",
            Path.home() / ".claude" / "settings.json",
        ]

        for path in candidates:
            if path.exists():
                return path
        return None

    # MCP Server Implementation Tests
    def test_mcp_server_exists(self) -> TestResult:
        """Check if MCP server file exists."""
        server_file = self.find_mcp_server_file()

        if server_file is None:
            return TestResult(
                name="MCP server implementation exists",
                passed=False,
                message="Create mcp_server.py in backend/app/",
                points=0.0,
                max_points=1.0
            )

        content = server_file.read_text(encoding='utf-8')
        line_count = len(content.splitlines())

        if line_count < 50:
            return TestResult(
                name="MCP server implementation exists",
                passed=False,
                message=f"Implementation too minimal ({line_count} lines)",
                points=0.5,
                max_points=1.0
            )

        return TestResult(
            name="MCP server implementation exists",
            passed=True,
            message=f"Found {server_file.name} ({line_count} lines)",
            points=1.0,
            max_points=1.0
        )

    def test_mcp_imports(self) -> TestResult:
        """Check if MCP dependencies are imported."""
        server_file = self.find_mcp_server_file()

        if server_file is None:
            return TestResult(
                name="MCP dependencies imported",
                passed=False,
                message="MCP server file not found",
                points=0.0,
                max_points=1.0
            )

        content = server_file.read_text(encoding='utf-8')
        imports = self.analyzer.check_mcp_imports(content)

        if not imports:
            return TestResult(
                name="MCP dependencies imported",
                passed=False,
                message="No MCP imports found. Add 'from mcp import ...'",
                points=0.0,
                max_points=1.0
            )

        return TestResult(
            name="MCP dependencies imported",
            passed=True,
            message=f"Found: {', '.join(imports[:3])}",
            points=1.0,
            max_points=1.0
        )

    def test_required_tools_defined(self) -> TestResult:
        """Check if all required tools are defined."""
        server_file = self.find_mcp_server_file()

        if server_file is None:
            return TestResult(
                name="Required MCP tools defined (4 tools)",
                passed=False,
                message="MCP server file not found",
                points=0.0,
                max_points=3.0
            )

        content = server_file.read_text(encoding='utf-8')

        found_tools = []
        for tool in MCPServerAnalyzer.REQUIRED_TOOLS:
            if tool in content.lower().replace("-", "_"):
                found_tools.append(tool)

        missing_tools = [t for t in MCPServerAnalyzer.REQUIRED_TOOLS if t not in found_tools]

        points = (len(found_tools) / len(MCPServerAnalyzer.REQUIRED_TOOLS)) * 3.0
        passed = len(found_tools) >= 3  # At least 3 of 4 tools

        message = f"Found {len(found_tools)}/4 tools"
        if missing_tools and self.verbose:
            message += f"\n   Missing: {', '.join(missing_tools)}"

        return TestResult(
            name="Required MCP tools defined (4 tools)",
            passed=passed,
            message=message,
            points=points,
            max_points=3.0
        )

    def test_rag_integration(self) -> TestResult:
        """Check if RAG service is integrated."""
        server_file = self.find_mcp_server_file()

        if server_file is None:
            return TestResult(
                name="RAG service integration",
                passed=False,
                message="MCP server file not found",
                points=0.0,
                max_points=1.5
            )

        content = server_file.read_text(encoding='utf-8')

        # Look for RAG-related patterns
        rag_indicators = [
            "rag_service",
            "RAGService",
            "search_documents",
            "retrieve",
            "azure_search",
            "vector_search",
            "semantic_search",
            "knowledge_base",
        ]

        found = [ind for ind in rag_indicators if ind.lower() in content.lower()]

        if len(found) >= 2:
            return TestResult(
                name="RAG service integration",
                passed=True,
                message=f"RAG integration detected: {', '.join(found[:3])}",
                points=1.5,
                max_points=1.5
            )
        elif len(found) >= 1:
            return TestResult(
                name="RAG service integration",
                passed=False,
                message=f"Partial RAG integration: {', '.join(found)}",
                points=0.75,
                max_points=1.5
            )

        return TestResult(
            name="RAG service integration",
            passed=False,
            message="No RAG service integration found",
            points=0.0,
            max_points=1.5
        )

    def test_mcp_main_entry(self) -> TestResult:
        """Check if MCP main entry point exists."""
        main_file = self.find_mcp_main_file()

        if main_file is None:
            return TestResult(
                name="MCP main entry point exists",
                passed=False,
                message="Create mcp_main.py as server entry point",
                points=0.0,
                max_points=0.5
            )

        content = main_file.read_text(encoding='utf-8')

        # Check for main execution pattern
        has_main = "__main__" in content or "run" in content.lower()

        if has_main:
            return TestResult(
                name="MCP main entry point exists",
                passed=True,
                message=f"Found {main_file.name}",
                points=0.5,
                max_points=0.5
            )

        return TestResult(
            name="MCP main entry point exists",
            passed=False,
            message="Entry point exists but missing main execution",
            points=0.25,
            max_points=0.5
        )

    # VS Code Integration Tests
    def test_vscode_mcp_config(self) -> TestResult:
        """Check if VS Code MCP configuration exists."""
        config_file = self.find_vscode_mcp_config()

        if config_file is None:
            return TestResult(
                name="VS Code MCP configuration exists",
                passed=False,
                message="Create .vscode/mcp.json with server configuration",
                points=0.0,
                max_points=1.0
            )

        try:
            content = json.loads(config_file.read_text(encoding='utf-8'))

            # Check for 47doors server configuration
            servers = content.get("mcpServers", content.get("servers", {}))
            has_47doors = (
                "47doors" in servers or
                "47doors" in str(content).lower()
            )

            if has_47doors:
                return TestResult(
                    name="VS Code MCP configuration exists",
                    passed=True,
                    message=f"Found 47doors server in {config_file.name}",
                    points=1.0,
                    max_points=1.0
                )

            return TestResult(
                name="VS Code MCP configuration exists",
                passed=False,
                message="Config exists but missing '47doors' server entry",
                points=0.5,
                max_points=1.0
            )

        except json.JSONDecodeError:
            return TestResult(
                name="VS Code MCP configuration exists",
                passed=False,
                message="Invalid JSON in config file",
                points=0.0,
                max_points=1.0
            )

    def test_dependencies_installed(self) -> TestResult:
        """Check if MCP dependencies are installed."""
        success, stdout, stderr = run_command(["pip", "show", "mcp"], timeout=10)

        if success:
            return TestResult(
                name="MCP Python package installed",
                passed=True,
                message="mcp package found",
                points=0.5,
                max_points=0.5
            )

        # Check requirements.txt for mcp
        requirements_path = self.project_root / "backend" / "requirements.txt"
        if requirements_path.exists():
            content = requirements_path.read_text(encoding='utf-8').lower()
            if "mcp" in content or "anthropic" in content:
                return TestResult(
                    name="MCP Python package installed",
                    passed=True,
                    message="mcp listed in requirements.txt",
                    points=0.5,
                    max_points=0.5
                )

        return TestResult(
            name="MCP Python package installed",
            passed=False,
            message="Install with: pip install 'mcp>=1.6.0'",
            points=0.0,
            max_points=0.5
        )

    def test_error_handling(self) -> TestResult:
        """Check if error handling is implemented."""
        server_file = self.find_mcp_server_file()

        if server_file is None:
            return TestResult(
                name="Error handling implemented",
                passed=False,
                message="MCP server file not found",
                points=0.0,
                max_points=1.0
            )

        content = server_file.read_text(encoding='utf-8')

        # Look for error handling patterns
        error_patterns = [
            "try:",
            "except",
            "raise",
            "Error",
            "Exception",
            "logging",
            "logger",
        ]

        found = [p for p in error_patterns if p in content]
        has_try_except = "try:" in content and "except" in content

        if has_try_except and len(found) >= 4:
            return TestResult(
                name="Error handling implemented",
                passed=True,
                message="Comprehensive error handling found",
                points=1.0,
                max_points=1.0
            )
        elif has_try_except:
            return TestResult(
                name="Error handling implemented",
                passed=True,
                message="Basic error handling found",
                points=0.75,
                max_points=1.0
            )
        elif found:
            return TestResult(
                name="Error handling implemented",
                passed=False,
                message=f"Partial: found {', '.join(found[:3])}",
                points=0.25,
                max_points=1.0
            )

        return TestResult(
            name="Error handling implemented",
            passed=False,
            message="Add try/except blocks for graceful error handling",
            points=0.0,
            max_points=1.0
        )

    def run_all_tests(self) -> tuple[float, float]:
        """Run all tests and return (points_earned, max_points)."""
        print("\n" + "=" * 60)
        print("Lab 07 - MCP Server (STRETCH GOAL): Verification")
        print("=" * 60)
        print("\u26a0\ufe0f  This lab is OPTIONAL. Skipping does not affect certification.")
        print("=" * 60 + "\n")

        # MCP Server Implementation
        print("MCP Server Implementation:")
        self.add_result(self.test_mcp_server_exists())
        self.add_result(self.test_mcp_imports())
        self.add_result(self.test_required_tools_defined())
        self.add_result(self.test_rag_integration())
        self.add_result(self.test_mcp_main_entry())

        # VS Code Integration
        print("\nVS Code Integration:")
        self.add_result(self.test_vscode_mcp_config())
        self.add_result(self.test_dependencies_installed())
        self.add_result(self.test_error_handling())

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
        print(f"Rubric score: {rubric_score:.1f}/10 (BONUS)")

        if rubric_score >= 8:
            print("\n\u2b50 EXEMPLARY - Outstanding MCP implementation!")
            print("   You have demonstrated advanced understanding of MCP protocols.")
        elif rubric_score >= 6:
            print("\n\u2705 PROFICIENT - MCP server working!")
            print("   Stretch goal completed successfully.")
        elif rubric_score >= 4:
            print("\n\u26a0\ufe0f DEVELOPING - Good progress on stretch goal")
            print("   Continue developing MCP implementation.")
        else:
            print("\n\u2139\ufe0f IN PROGRESS - Stretch goal started")
            print("   Remember: This is optional. Labs 00-06 are sufficient for certification.")

        print("\n" + "=" * 60)
        print("\nTo test VS Code integration:")
        print("  1. Open VS Code with this project")
        print("  2. Open Copilot Chat (Ctrl+Shift+I)")
        print("  3. Type '@' and look for '47doors'")
        print("  4. Try: @47doors What is the deadline for housing applications?")
        print("=" * 60)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    runner = TestRunner(verbose=verbose)
    points_earned, max_points = runner.run_all_tests()
    runner.print_summary(points_earned, max_points)

    # Return 0 always for stretch goal (never fails the build)
    return 0


if __name__ == "__main__":
    sys.exit(main())

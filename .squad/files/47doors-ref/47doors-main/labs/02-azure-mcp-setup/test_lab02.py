#!/usr/bin/env python3
"""
Lab 02 - Azure MCP Setup: Verification Script

Tests MCP server installation, Azure CLI authentication, and configuration.
Run this script to verify Lab 02 is complete.

Usage:
    python test_lab02.py [--verbose]
"""

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


class TestRunner:
    """Runs Lab 02 verification tests."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []
        self.lab_dir = Path(__file__).parent
        self.project_root = self.lab_dir.parent.parent

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

    def test_azure_cli_installed(self) -> TestResult:
        """Check if Azure CLI is installed."""
        success, stdout, stderr = run_command(["az", "--version"])

        if not success:
            return TestResult(
                name="Azure CLI installed",
                passed=False,
                message="Azure CLI not found. Install from https://aka.ms/installazurecli",
                points=0.0,
                max_points=1.0
            )

        # Parse version
        version_match = re.search(r"azure-cli\s+(\d+\.\d+\.\d+)", stdout)
        version = version_match.group(1) if version_match else "unknown"

        return TestResult(
            name="Azure CLI installed",
            passed=True,
            message=f"Version {version}",
            points=1.0,
            max_points=1.0
        )

    def test_azure_cli_authenticated(self) -> TestResult:
        """Check if user is logged into Azure CLI."""
        success, stdout, stderr = run_command(["az", "account", "show"])

        if not success:
            return TestResult(
                name="Azure CLI authenticated",
                passed=False,
                message="Not logged in. Run 'az login' to authenticate.",
                points=0.0,
                max_points=1.0
            )

        try:
            account = json.loads(stdout)
            user = account.get("user", {}).get("name", "unknown")
            subscription = account.get("name", "unknown")
            return TestResult(
                name="Azure CLI authenticated",
                passed=True,
                message=f"Logged in as {user} (subscription: {subscription[:30]}...)",
                points=1.0,
                max_points=1.0
            )
        except json.JSONDecodeError:
            return TestResult(
                name="Azure CLI authenticated",
                passed=True,
                message="Logged in (could not parse account details)",
                points=1.0,
                max_points=1.0
            )

    def test_node_js_installed(self) -> TestResult:
        """Check if Node.js is installed (required for npx)."""
        success, stdout, stderr = run_command(["node", "--version"])

        if not success:
            return TestResult(
                name="Node.js installed",
                passed=False,
                message="Node.js not found. Install from https://nodejs.org/",
                points=0.0,
                max_points=0.5
            )

        # Parse version
        match = re.match(r"v?(\d+)", stdout)
        major = int(match.group(1)) if match else 0

        if major < 18:
            return TestResult(
                name="Node.js installed",
                passed=False,
                message=f"Version {stdout} (need 18+)",
                points=0.0,
                max_points=0.5
            )

        return TestResult(
            name="Node.js installed",
            passed=True,
            message=f"Version {stdout}",
            points=0.5,
            max_points=0.5
        )

    def test_mcp_server_available(self) -> TestResult:
        """Check if Azure MCP server package is available."""
        success, stdout, stderr = run_command(
            ["npx", "-y", "@azure/mcp@latest", "--version"],
            timeout=60
        )

        if success:
            return TestResult(
                name="Azure MCP Server available",
                passed=True,
                message=f"MCP package accessible via npx",
                points=1.0,
                max_points=1.0
            )

        # Try alternative package name
        success, stdout, stderr = run_command(
            ["npm", "view", "@azure/mcp-server", "version"],
            timeout=30
        )

        if success and stdout:
            return TestResult(
                name="Azure MCP Server available",
                passed=True,
                message=f"Version {stdout} available",
                points=1.0,
                max_points=1.0
            )

        return TestResult(
            name="Azure MCP Server available",
            passed=False,
            message="MCP server package not found. Check npm connectivity.",
            points=0.0,
            max_points=1.0
        )

    def test_mcp_config_exists(self) -> TestResult:
        """Check if MCP configuration file exists."""
        config_locations = [
            self.project_root / ".claude" / "settings.local.json",
            self.project_root / ".vscode" / "mcp.json",
            Path.home() / ".claude" / "settings.json",
        ]

        for config_path in config_locations:
            if config_path.exists():
                try:
                    content = json.loads(config_path.read_text())

                    # Check for MCP server configuration
                    has_mcp = (
                        "mcpServers" in content or
                        "mcp" in str(content).lower() or
                        "servers" in content
                    )

                    if has_mcp:
                        return TestResult(
                            name="MCP configuration file exists",
                            passed=True,
                            message=f"Found at {config_path}",
                            points=1.0,
                            max_points=1.0
                        )
                except json.JSONDecodeError:
                    self.log(f"Invalid JSON in {config_path}")
                except Exception as e:
                    self.log(f"Error reading {config_path}: {e}")

        return TestResult(
            name="MCP configuration file exists",
            passed=False,
            message="No MCP configuration found. Check .claude/settings.local.json or .vscode/mcp.json",
            points=0.0,
            max_points=1.0
        )

    def test_mcp_config_valid(self) -> TestResult:
        """Check if MCP configuration is valid."""
        config_locations = [
            self.project_root / ".claude" / "settings.local.json",
            self.project_root / ".vscode" / "mcp.json",
            Path.home() / ".claude" / "settings.json",
        ]

        for config_path in config_locations:
            if not config_path.exists():
                continue

            try:
                content = json.loads(config_path.read_text())

                # Check for proper structure
                mcp_servers = content.get("mcpServers", {})
                if not mcp_servers:
                    mcp_servers = content.get("servers", {})

                azure_config = mcp_servers.get("azure") or mcp_servers.get("@azure")

                if azure_config:
                    # Verify it has command or args
                    has_command = "command" in azure_config or "args" in azure_config
                    if has_command:
                        return TestResult(
                            name="MCP configuration is valid",
                            passed=True,
                            message=f"Azure MCP server configured in {config_path.name}",
                            points=1.0,
                            max_points=1.0
                        )

            except json.JSONDecodeError:
                continue
            except Exception:
                continue

        return TestResult(
            name="MCP configuration is valid",
            passed=False,
            message="Azure MCP server not properly configured",
            points=0.0,
            max_points=1.0
        )

    def test_environment_variables(self) -> TestResult:
        """Check if required Azure environment variables are set."""
        required_vars = [
            "AZURE_SUBSCRIPTION_ID",
        ]
        optional_vars = [
            "AZURE_TENANT_ID",
            "AZURE_CLIENT_ID",
        ]

        # Check environment variables
        found_required = []
        found_optional = []

        for var in required_vars:
            if os.environ.get(var):
                found_required.append(var)

        for var in optional_vars:
            if os.environ.get(var):
                found_optional.append(var)

        # Also check if az CLI can provide subscription
        if not found_required:
            success, stdout, stderr = run_command(["az", "account", "show", "--query", "id", "-o", "tsv"])
            if success and stdout:
                found_required.append("AZURE_SUBSCRIPTION_ID (via az CLI)")

        if found_required:
            message = f"Found: {', '.join(found_required)}"
            if found_optional:
                message += f" + {len(found_optional)} optional vars"
            return TestResult(
                name="Azure environment variables configured",
                passed=True,
                message=message,
                points=0.5,
                max_points=0.5
            )

        return TestResult(
            name="Azure environment variables configured",
            passed=False,
            message="Set AZURE_SUBSCRIPTION_ID or ensure az login provides subscription",
            points=0.0,
            max_points=0.5
        )

    def test_can_list_subscriptions(self) -> TestResult:
        """Test if Azure subscriptions can be listed."""
        success, stdout, stderr = run_command(
            ["az", "account", "list", "--query", "[].{name:name,id:id}", "-o", "json"],
            timeout=30
        )

        if not success:
            return TestResult(
                name="Can list Azure subscriptions",
                passed=False,
                message=f"Failed to list subscriptions: {stderr[:100]}",
                points=0.0,
                max_points=1.0
            )

        try:
            subscriptions = json.loads(stdout)
            count = len(subscriptions)

            if count == 0:
                return TestResult(
                    name="Can list Azure subscriptions",
                    passed=False,
                    message="No subscriptions found. Check your Azure account permissions.",
                    points=0.5,
                    max_points=1.0
                )

            return TestResult(
                name="Can list Azure subscriptions",
                passed=True,
                message=f"Found {count} subscription(s)",
                points=1.0,
                max_points=1.0
            )
        except json.JSONDecodeError:
            return TestResult(
                name="Can list Azure subscriptions",
                passed=False,
                message="Could not parse subscription list",
                points=0.0,
                max_points=1.0
            )

    def test_can_list_resource_groups(self) -> TestResult:
        """Test if Azure resource groups can be listed."""
        success, stdout, stderr = run_command(
            ["az", "group", "list", "--query", "[].{name:name,location:location}", "-o", "json"],
            timeout=30
        )

        if not success:
            return TestResult(
                name="Can list Azure resource groups",
                passed=False,
                message=f"Failed to list resource groups: {stderr[:100]}",
                points=0.0,
                max_points=1.0
            )

        try:
            groups = json.loads(stdout)
            count = len(groups)

            if count == 0:
                return TestResult(
                    name="Can list Azure resource groups",
                    passed=True,
                    message="No resource groups found (subscription may be empty)",
                    points=0.5,
                    max_points=1.0
                )

            # Show first few groups
            group_names = [g.get("name", "unknown") for g in groups[:3]]
            return TestResult(
                name="Can list Azure resource groups",
                passed=True,
                message=f"Found {count} group(s): {', '.join(group_names)}...",
                points=1.0,
                max_points=1.0
            )
        except json.JSONDecodeError:
            return TestResult(
                name="Can list Azure resource groups",
                passed=False,
                message="Could not parse resource groups",
                points=0.0,
                max_points=1.0
            )

    def test_setup_documented(self) -> TestResult:
        """Check if setup steps are documented."""
        doc_locations = [
            self.lab_dir / "exercises" / "setup_notes.md",
            self.lab_dir / "exercises" / "setup.md",
            self.lab_dir / "my_setup.md",
            self.lab_dir / "notes.md",
        ]

        for doc_path in doc_locations:
            if doc_path.exists():
                content = doc_path.read_text(encoding='utf-8')
                word_count = len(content.split())

                if word_count >= 50:
                    return TestResult(
                        name="Setup steps documented",
                        passed=True,
                        message=f"Found documentation at {doc_path.name} ({word_count} words)",
                        points=0.5,
                        max_points=0.5
                    )

        return TestResult(
            name="Setup steps documented",
            passed=False,
            message="Create setup_notes.md in exercises/ with your setup steps",
            points=0.0,
            max_points=0.5
        )

    def run_all_tests(self) -> tuple[float, float]:
        """Run all tests and return (points_earned, max_points)."""
        print("\n" + "=" * 60)
        print("Lab 02 - Azure MCP Setup: Verification")
        print("=" * 60 + "\n")

        # Prerequisites
        print("Prerequisites:")
        self.add_result(self.test_azure_cli_installed())
        self.add_result(self.test_azure_cli_authenticated())
        self.add_result(self.test_node_js_installed())

        # MCP Server
        print("\nMCP Server Configuration:")
        self.add_result(self.test_mcp_server_available())
        self.add_result(self.test_mcp_config_exists())
        self.add_result(self.test_mcp_config_valid())
        self.add_result(self.test_environment_variables())

        # Azure Integration
        print("\nAzure Integration:")
        self.add_result(self.test_can_list_subscriptions())
        self.add_result(self.test_can_list_resource_groups())

        # Documentation
        print("\nDocumentation:")
        self.add_result(self.test_setup_documented())

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

        # Calculate rubric score (out of 5)
        rubric_score = min(5, (points_earned / max_points) * 5) if max_points > 0 else 0

        print(f"\nTests passed: {passed}/{total}")
        print(f"Points earned: {points_earned:.1f}/{max_points:.1f}")
        print(f"Rubric score: {rubric_score:.1f}/5")

        if rubric_score >= 4:
            print("\n\u2705 EXEMPLARY - MCP setup complete!")
        elif rubric_score >= 3:
            print("\n\u2705 PROFICIENT - Lab 02 complete!")
        elif rubric_score >= 2:
            print("\n\u26a0\ufe0f DEVELOPING - Some configuration needed")
        else:
            print("\n\u274c BEGINNING - Please complete MCP setup")

        print("\n" + "=" * 60)
        print("\nNote: To fully test @azure queries, open VS Code and try:")
        print("  @azure List my subscriptions")
        print("  @azure What resource groups do I have?")
        print("=" * 60)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    runner = TestRunner(verbose=verbose)
    points_earned, max_points = runner.run_all_tests()
    runner.print_summary(points_earned, max_points)

    # Return exit code based on pass/fail
    rubric_score = (points_earned / max_points) * 5 if max_points > 0 else 0
    return 0 if rubric_score >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())

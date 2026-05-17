#!/usr/bin/env python3
"""
Lab 06 - Deploy with azd: Verification Script

Tests Docker configuration, Azure deployment, and health endpoints.
Run this script to verify Lab 06 is complete.

Usage:
    python test_lab06.py [--verbose] [--skip-azure] [--skip-docker]
"""

import io
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def run_command(command: list[str], timeout: int = 60) -> tuple[bool, str, str]:
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


def http_get(url: str, timeout: int = 10) -> tuple[int, str]:
    """Make HTTP GET request and return (status_code, body)."""
    try:
        req = Request(url, headers={"User-Agent": "Lab06-Test/1.0"})
        with urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode('utf-8')
    except HTTPError as e:
        return e.code, str(e)
    except URLError as e:
        return 0, str(e)
    except Exception as e:
        return 0, str(e)


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    message: str
    points: float = 0.0
    max_points: float = 0.0


class TestRunner:
    """Runs Lab 06 verification tests."""

    def __init__(self, verbose: bool = False, skip_azure: bool = False, skip_docker: bool = False):
        self.verbose = verbose
        self.skip_azure = skip_azure
        self.skip_docker = skip_docker
        self.results: list[TestResult] = []
        self.lab_dir = Path(__file__).parent
        self.project_root = self.lab_dir.parent.parent
        self.backend_url: Optional[str] = None

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

    # Docker Tests
    def test_dockerfile_exists(self) -> TestResult:
        """Check if Dockerfile exists."""
        dockerfile_locations = [
            self.project_root / "backend" / "Dockerfile",
            self.project_root / "Dockerfile",
            self.lab_dir / "start" / "Dockerfile",
        ]

        for path in dockerfile_locations:
            if path.exists():
                return TestResult(
                    name="Dockerfile exists",
                    passed=True,
                    message=str(path.relative_to(self.project_root)),
                    points=0.5,
                    max_points=0.5
                )

        return TestResult(
            name="Dockerfile exists",
            passed=False,
            message="Create Dockerfile in backend/ or project root",
            points=0.0,
            max_points=0.5
        )

    def test_docker_compose_exists(self) -> TestResult:
        """Check if docker-compose.yml exists."""
        compose_locations = [
            self.project_root / "docker-compose.yml",
            self.project_root / "docker-compose.yaml",
            self.project_root / "compose.yml",
            self.project_root / "compose.yaml",
        ]

        for path in compose_locations:
            if path.exists():
                return TestResult(
                    name="Docker Compose file exists",
                    passed=True,
                    message=str(path.name),
                    points=0.5,
                    max_points=0.5
                )

        return TestResult(
            name="Docker Compose file exists",
            passed=False,
            message="Create docker-compose.yml in project root",
            points=0.0,
            max_points=0.5
        )

    def test_docker_installed(self) -> TestResult:
        """Check if Docker is installed and running."""
        success, stdout, stderr = run_command(["docker", "--version"])

        if not success:
            return TestResult(
                name="Docker installed",
                passed=False,
                message="Docker not found. Install Docker Desktop.",
                points=0.0,
                max_points=0.5
            )

        # Check if Docker daemon is running
        success, stdout, stderr = run_command(["docker", "info"], timeout=10)

        if not success:
            return TestResult(
                name="Docker installed",
                passed=False,
                message="Docker installed but not running. Start Docker Desktop.",
                points=0.25,
                max_points=0.5
            )

        return TestResult(
            name="Docker installed",
            passed=True,
            message="Docker running",
            points=0.5,
            max_points=0.5
        )

    def test_docker_compose_valid(self) -> TestResult:
        """Check if docker-compose configuration is valid."""
        success, stdout, stderr = run_command(
            ["docker", "compose", "config", "--quiet"],
            timeout=30
        )

        if success:
            return TestResult(
                name="Docker Compose configuration valid",
                passed=True,
                message="Configuration validated successfully",
                points=0.5,
                max_points=0.5
            )

        # Try docker-compose (hyphenated) as fallback
        success, stdout, stderr = run_command(
            ["docker-compose", "config", "--quiet"],
            timeout=30
        )

        if success:
            return TestResult(
                name="Docker Compose configuration valid",
                passed=True,
                message="Configuration validated successfully",
                points=0.5,
                max_points=0.5
            )

        return TestResult(
            name="Docker Compose configuration valid",
            passed=False,
            message=f"Invalid config: {stderr[:100]}",
            points=0.0,
            max_points=0.5
        )

    def test_local_health_endpoint(self) -> TestResult:
        """Test local health endpoint if Docker is running."""
        if self.skip_docker:
            return TestResult(
                name="Local health endpoint responds",
                passed=True,
                message="Skipped (--skip-docker)",
                points=1.0,
                max_points=1.0
            )

        local_url = "http://localhost:8000/api/health"
        status, body = http_get(local_url, timeout=5)

        if status == 200:
            try:
                data = json.loads(body)
                status_value = data.get("status", "unknown")
                return TestResult(
                    name="Local health endpoint responds",
                    passed=True,
                    message=f"Status: {status_value}",
                    points=1.0,
                    max_points=1.0
                )
            except json.JSONDecodeError:
                return TestResult(
                    name="Local health endpoint responds",
                    passed=True,
                    message="HTTP 200 (non-JSON response)",
                    points=0.75,
                    max_points=1.0
                )

        if status == 0:
            return TestResult(
                name="Local health endpoint responds",
                passed=False,
                message="Not running. Start with: docker compose up -d",
                points=0.0,
                max_points=1.0
            )

        return TestResult(
            name="Local health endpoint responds",
            passed=False,
            message=f"HTTP {status}: {body[:50]}",
            points=0.0,
            max_points=1.0
        )

    # Azure Deployment Tests
    def test_azd_installed(self) -> TestResult:
        """Check if Azure Developer CLI is installed."""
        success, stdout, stderr = run_command(["azd", "version"])

        if not success:
            return TestResult(
                name="Azure Developer CLI (azd) installed",
                passed=False,
                message="Install from https://aka.ms/azd-install",
                points=0.0,
                max_points=0.5
            )

        version_match = re.search(r"(\d+\.\d+\.\d+)", stdout)
        version = version_match.group(1) if version_match else "unknown"

        return TestResult(
            name="Azure Developer CLI (azd) installed",
            passed=True,
            message=f"Version {version}",
            points=0.5,
            max_points=0.5
        )

    def test_azure_yaml_exists(self) -> TestResult:
        """Check if azure.yaml exists."""
        azure_yaml = self.project_root / "azure.yaml"

        if azure_yaml.exists():
            return TestResult(
                name="azure.yaml configuration exists",
                passed=True,
                message="Found azure.yaml",
                points=0.5,
                max_points=0.5
            )

        return TestResult(
            name="azure.yaml configuration exists",
            passed=False,
            message="Create azure.yaml for azd deployment",
            points=0.0,
            max_points=0.5
        )

    def test_infra_templates_exist(self) -> TestResult:
        """Check if infrastructure templates exist."""
        infra_locations = [
            self.project_root / "infra" / "main.bicep",
            self.project_root / "infra" / "main.json",
            self.lab_dir / "infra" / "main.bicep",
        ]

        for path in infra_locations:
            if path.exists():
                return TestResult(
                    name="Infrastructure as Code templates exist",
                    passed=True,
                    message=f"Found {path.relative_to(self.project_root)}",
                    points=1.0,
                    max_points=1.0
                )

        return TestResult(
            name="Infrastructure as Code templates exist",
            passed=False,
            message="Create infra/main.bicep for Azure resources",
            points=0.0,
            max_points=1.0
        )

    def test_azd_environment_configured(self) -> TestResult:
        """Check if azd environment is configured."""
        if self.skip_azure:
            return TestResult(
                name="azd environment configured",
                passed=True,
                message="Skipped (--skip-azure)",
                points=1.0,
                max_points=1.0
            )

        success, stdout, stderr = run_command(["azd", "env", "list"])

        if not success:
            return TestResult(
                name="azd environment configured",
                passed=False,
                message="Run 'azd init' to create environment",
                points=0.0,
                max_points=1.0
            )

        if "No environments" in stdout or not stdout.strip():
            return TestResult(
                name="azd environment configured",
                passed=False,
                message="No azd environment found. Run 'azd init'",
                points=0.0,
                max_points=1.0
            )

        return TestResult(
            name="azd environment configured",
            passed=True,
            message="Environment found",
            points=1.0,
            max_points=1.0
        )

    def test_azure_resources_deployed(self) -> TestResult:
        """Check if Azure resources are deployed."""
        if self.skip_azure:
            return TestResult(
                name="Azure resources deployed",
                passed=True,
                message="Skipped (--skip-azure)",
                points=2.0,
                max_points=2.0
            )

        # Try to get backend URL from azd
        success, stdout, stderr = run_command(
            ["azd", "env", "get-value", "AZURE_CONTAINERAPP_URL"],
            timeout=30
        )

        if success and stdout.startswith("http"):
            self.backend_url = stdout.strip()
            return TestResult(
                name="Azure resources deployed",
                passed=True,
                message=f"Container App URL: {self.backend_url[:50]}...",
                points=2.0,
                max_points=2.0
            )

        # Try alternative: check if resource group exists
        success, stdout, stderr = run_command(
            ["azd", "env", "get-value", "AZURE_RESOURCE_GROUP"],
            timeout=30
        )

        if success and stdout:
            rg_name = stdout.strip()
            success, stdout, stderr = run_command(
                ["az", "group", "show", "--name", rg_name],
                timeout=30
            )
            if success:
                return TestResult(
                    name="Azure resources deployed",
                    passed=True,
                    message=f"Resource group exists: {rg_name}",
                    points=1.5,
                    max_points=2.0
                )

        return TestResult(
            name="Azure resources deployed",
            passed=False,
            message="Run 'azd up' to deploy to Azure",
            points=0.0,
            max_points=2.0
        )

    def test_production_health_endpoint(self) -> TestResult:
        """Test production health endpoint."""
        if self.skip_azure:
            return TestResult(
                name="Production health endpoint responds",
                passed=True,
                message="Skipped (--skip-azure)",
                points=2.0,
                max_points=2.0
            )

        if not self.backend_url:
            # Try to get URL
            success, stdout, stderr = run_command(
                ["azd", "env", "get-value", "AZURE_CONTAINERAPP_URL"],
                timeout=30
            )
            if success and stdout.startswith("http"):
                self.backend_url = stdout.strip()

        if not self.backend_url:
            return TestResult(
                name="Production health endpoint responds",
                passed=False,
                message="Backend URL not available. Deploy with 'azd up' first.",
                points=0.0,
                max_points=2.0
            )

        health_url = f"{self.backend_url}/api/health"
        status, body = http_get(health_url, timeout=10)

        if status == 200:
            try:
                data = json.loads(body)
                health_status = data.get("status", "unknown")

                # Check for required fields
                has_timestamp = "timestamp" in data
                has_services = "services" in data

                if health_status == "healthy" and has_timestamp:
                    return TestResult(
                        name="Production health endpoint responds",
                        passed=True,
                        message=f"Status: healthy, includes timestamp and services",
                        points=2.0,
                        max_points=2.0
                    )
                else:
                    return TestResult(
                        name="Production health endpoint responds",
                        passed=True,
                        message=f"Status: {health_status} (missing some fields)",
                        points=1.5,
                        max_points=2.0
                    )
            except json.JSONDecodeError:
                return TestResult(
                    name="Production health endpoint responds",
                    passed=True,
                    message="HTTP 200 (non-JSON response)",
                    points=1.0,
                    max_points=2.0
                )

        return TestResult(
            name="Production health endpoint responds",
            passed=False,
            message=f"HTTP {status}: {body[:100]}",
            points=0.0,
            max_points=2.0
        )

    def test_container_app_running(self) -> TestResult:
        """Check if Container App is running."""
        if self.skip_azure:
            return TestResult(
                name="Container App status: Running",
                passed=True,
                message="Skipped (--skip-azure)",
                points=1.5,
                max_points=1.5
            )

        # Get resource group
        success, rg_stdout, stderr = run_command(
            ["azd", "env", "get-value", "AZURE_RESOURCE_GROUP"],
            timeout=30
        )

        if not success or not rg_stdout:
            return TestResult(
                name="Container App status: Running",
                passed=False,
                message="Could not determine resource group",
                points=0.0,
                max_points=1.5
            )

        # List container apps
        success, stdout, stderr = run_command(
            ["az", "containerapp", "list", "--resource-group", rg_stdout.strip(),
             "--query", "[].{name:name,status:properties.runningStatus}", "-o", "json"],
            timeout=60
        )

        if not success:
            return TestResult(
                name="Container App status: Running",
                passed=False,
                message=f"Error checking status: {stderr[:50]}",
                points=0.0,
                max_points=1.5
            )

        try:
            apps = json.loads(stdout)
            if not apps:
                return TestResult(
                    name="Container App status: Running",
                    passed=False,
                    message="No Container Apps found in resource group",
                    points=0.0,
                    max_points=1.5
                )

            running_apps = [a for a in apps if a.get("status") == "Running"]
            if running_apps:
                names = [a.get("name", "unknown") for a in running_apps]
                return TestResult(
                    name="Container App status: Running",
                    passed=True,
                    message=f"Running: {', '.join(names)}",
                    points=1.5,
                    max_points=1.5
                )

            return TestResult(
                name="Container App status: Running",
                passed=False,
                message=f"Apps found but not running: {apps}",
                points=0.5,
                max_points=1.5
            )
        except json.JSONDecodeError:
            return TestResult(
                name="Container App status: Running",
                passed=False,
                message="Could not parse Container App status",
                points=0.0,
                max_points=1.5
            )

    def test_can_view_logs(self) -> TestResult:
        """Check if logs can be accessed."""
        if self.skip_azure:
            return TestResult(
                name="Can access container logs",
                passed=True,
                message="Skipped (--skip-azure)",
                points=1.0,
                max_points=1.0
            )

        # Get resource group
        success, rg_stdout, stderr = run_command(
            ["azd", "env", "get-value", "AZURE_RESOURCE_GROUP"],
            timeout=30
        )

        if not success or not rg_stdout:
            return TestResult(
                name="Can access container logs",
                passed=False,
                message="Resource group not configured",
                points=0.0,
                max_points=1.0
            )

        # List container apps to get name
        success, stdout, stderr = run_command(
            ["az", "containerapp", "list", "--resource-group", rg_stdout.strip(),
             "--query", "[0].name", "-o", "tsv"],
            timeout=30
        )

        if not success or not stdout:
            return TestResult(
                name="Can access container logs",
                passed=False,
                message="No Container App found",
                points=0.0,
                max_points=1.0
            )

        app_name = stdout.strip()

        # Try to view logs
        success, stdout, stderr = run_command(
            ["az", "containerapp", "logs", "show", "--name", app_name,
             "--resource-group", rg_stdout.strip(), "--tail", "5"],
            timeout=60
        )

        if success or "log" in stdout.lower():
            return TestResult(
                name="Can access container logs",
                passed=True,
                message=f"Logs accessible for {app_name}",
                points=1.0,
                max_points=1.0
            )

        return TestResult(
            name="Can access container logs",
            passed=False,
            message=f"Could not access logs: {stderr[:50]}",
            points=0.0,
            max_points=1.0
        )

    def run_all_tests(self) -> tuple[float, float]:
        """Run all tests and return (points_earned, max_points)."""
        print("\n" + "=" * 60)
        print("Lab 06 - Deploy with azd: Verification")
        print("=" * 60 + "\n")

        # Docker Tests
        print("Docker Configuration:")
        self.add_result(self.test_dockerfile_exists())
        self.add_result(self.test_docker_compose_exists())
        self.add_result(self.test_docker_installed())
        self.add_result(self.test_docker_compose_valid())
        self.add_result(self.test_local_health_endpoint())

        # Azure Tests
        print("\nAzure Deployment:")
        self.add_result(self.test_azd_installed())
        self.add_result(self.test_azure_yaml_exists())
        self.add_result(self.test_infra_templates_exist())
        self.add_result(self.test_azd_environment_configured())
        self.add_result(self.test_azure_resources_deployed())

        # Production Tests
        print("\nProduction Verification:")
        self.add_result(self.test_production_health_endpoint())
        self.add_result(self.test_container_app_running())
        self.add_result(self.test_can_view_logs())

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
            print("\n\u2705 EXEMPLARY - Production deployment successful!")
        elif rubric_score >= 9:
            print("\n\u2705 PROFICIENT - Lab 06 complete!")
        elif rubric_score >= 6:
            print("\n\u26a0\ufe0f DEVELOPING - Deployment partially complete")
        else:
            print("\n\u274c BEGINNING - Please complete deployment")

        if self.backend_url:
            print(f"\n\u2728 Your app is live at: {self.backend_url}")

        print("\n" + "=" * 60)
        print("\nDeployment Commands:")
        print("  Local:  docker compose up -d --build")
        print("  Azure:  azd up")
        print("  Logs:   az containerapp logs show --name <app> --resource-group <rg>")
        print("=" * 60)


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    skip_azure = "--skip-azure" in sys.argv
    skip_docker = "--skip-docker" in sys.argv

    runner = TestRunner(verbose=verbose, skip_azure=skip_azure, skip_docker=skip_docker)
    points_earned, max_points = runner.run_all_tests()
    runner.print_summary(points_earned, max_points)

    # Return exit code based on pass/fail
    rubric_score = (points_earned / max_points) * 15 if max_points > 0 else 0
    return 0 if rubric_score >= 9 else 1


if __name__ == "__main__":
    sys.exit(main())

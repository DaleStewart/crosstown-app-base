#!/usr/bin/env python3
"""
Environment verification script for the 47 Doors boot camp.

Checks all required tools and configurations are in place before starting.
"""

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def run_command(command: list[str], timeout: int = 30) -> tuple[bool, str, str]:
    """
    Run a command and return (success, stdout, stderr).

    Args:
        command: Command and arguments as a list
        timeout: Maximum seconds to wait for command

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(sys.platform == "win32"),  # Shell needed on Windows for some commands
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", "Command not found"
    except Exception as e:
        return False, "", str(e)


def check_python_version() -> tuple[str, str, bool]:
    """Check Python version is >= 3.11."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 11:
        return "pass", f"Python {version_str}", True
    else:
        return "fail", f"Python {version_str} (need >= 3.11)", False


def check_node_version() -> tuple[str, str, bool]:
    """Check Node.js version is >= 18."""
    success, stdout, stderr = run_command(["node", "--version"])

    if not success:
        return "fail", "Node.js not found - install from https://nodejs.org/", False

    # Parse version like "v18.17.0"
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", stdout)
    if match:
        major = int(match.group(1))
        version_str = stdout.lstrip("v")
        if major >= 18:
            return "pass", f"Node.js {version_str}", True
        else:
            return "fail", f"Node.js {version_str} (need >= 18)", False

    return "warn", f"Node.js version unknown: {stdout}", False


def check_azure_cli() -> tuple[str, str, bool]:
    """Check Azure CLI is installed and user is logged in."""
    # First check if az is installed
    success, stdout, stderr = run_command(["az", "--version"])
    if not success:
        return "fail", "Azure CLI not found - install from https://aka.ms/installazurecliwindows", False

    # Parse version from output
    version_match = re.search(r"azure-cli\s+(\d+\.\d+\.\d+)", stdout)
    version_str = version_match.group(1) if version_match else "unknown"

    # Check if logged in
    success, stdout, stderr = run_command(["az", "account", "show"])
    if not success:
        return "fail", f"Azure CLI {version_str} (not logged in - run 'az login')", False

    # Parse account info
    try:
        account = json.loads(stdout)
        user = account.get("user", {}).get("name", "unknown")
        return "pass", f"Azure CLI {version_str} (logged in as {user})", True
    except json.JSONDecodeError:
        return "warn", f"Azure CLI {version_str} (logged in)", True


def check_azd() -> tuple[str, str, bool]:
    """Check Azure Developer CLI is installed."""
    success, stdout, stderr = run_command(["azd", "version"])

    if not success:
        return "fail", "azd not found - install from https://aka.ms/azd-install", False

    # Parse version like "azd version 1.5.0 (commit abc123)"
    match = re.search(r"(\d+\.\d+\.\d+)", stdout)
    version_str = match.group(1) if match else stdout

    return "pass", f"azd {version_str}", True


def check_docker() -> tuple[str, str, bool]:
    """Check Docker is installed and running."""
    # Check if docker command exists
    success, stdout, stderr = run_command(["docker", "--version"])
    if not success:
        return "fail", "Docker not found - install Docker Desktop", False

    # Check if Docker daemon is running
    success, stdout, stderr = run_command(["docker", "info"], timeout=10)
    if not success:
        if "permission denied" in stderr.lower():
            return "fail", "Docker installed but permission denied (add user to docker group)", False
        elif "cannot connect" in stderr.lower() or "error during connect" in stderr.lower():
            return "fail", "Docker installed but not running (start Docker Desktop)", False
        else:
            return "fail", f"Docker not responding: {stderr[:100]}", False

    return "pass", "Docker Desktop running", True


def check_env_file() -> tuple[str, str, bool]:
    """Check .env file exists and has required variables."""
    # Look for .env in project root (two levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    env_path = project_root / ".env"

    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
    ]

    optional_vars = [
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
    ]

    if not env_path.exists():
        # Check for .env.example
        example_path = project_root / ".env.example"
        if example_path.exists():
            return "warn", f".env not found (copy from .env.example)", False
        return "warn", ".env not found (using mock mode)", False

    # Read and parse .env file
    env_vars = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip().strip('"').strip("'")

    # Check for missing required variables
    missing = []
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing.append(var)

    if missing:
        return "warn", f".env missing {', '.join(missing)} (using mock mode)", False

    return "pass", ".env configured with Azure credentials", True


def check_health_endpoint() -> tuple[str, str, bool]:
    """Check if backend health endpoint is reachable."""
    import urllib.request
    import urllib.error

    url = "http://localhost:8000/api/health"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                return "pass", "Backend /api/health responding", True
            else:
                return "warn", f"Backend returned status {response.status}", False
    except urllib.error.URLError:
        return "skip", "Health check skipped (backend not running)", True
    except Exception as e:
        return "skip", f"Health check skipped ({str(e)[:50]})", True


def print_result(status: str, message: str) -> None:
    """Print a check result with appropriate icon."""
    icons = {
        "pass": "\u2705",  # Green check
        "fail": "\u274c",  # Red X
        "warn": "\u26a0\ufe0f",   # Warning
        "skip": "\u23ed\ufe0f",   # Skip
    }
    icon = icons.get(status, "\u2753")  # Question mark for unknown
    print(f"{icon}  {message}")


def main() -> int:
    """Run all environment checks and report results."""
    print("\n47 Doors Boot Camp - Environment Verification\n")
    print("=" * 50)
    print()

    checks = [
        ("Python", check_python_version),
        ("Node.js", check_node_version),
        ("Azure CLI", check_azure_cli),
        ("Azure Developer CLI", check_azd),
        ("Docker", check_docker),
        ("Environment File", check_env_file),
        ("Health Endpoint", check_health_endpoint),
    ]

    results = []
    for name, check_func in checks:
        try:
            status, message, passed = check_func()
            results.append((status, passed))
            print_result(status, message)
        except Exception as e:
            results.append(("fail", False))
            print_result("fail", f"{name}: Unexpected error - {str(e)[:50]}")

    print()
    print("=" * 50)

    # Calculate summary
    total = len(results)
    passed = sum(1 for status, p in results if p)
    failed = sum(1 for status, p in results if status == "fail")

    print()
    if failed == 0:
        print(f"Ready for boot camp! ({passed}/{total} checks passed)")
        return 0
    else:
        print(f"Some issues found ({passed}/{total} checks passed)")
        print("\nPlease resolve the failed checks before proceeding.")
        print("Run this script again after fixing issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

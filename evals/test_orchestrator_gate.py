"""Pytest wrapper so CI fails the build when the orchestrator-level eval fails."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


@pytest.mark.orchestrator_gate
def test_orchestrator_eval_gate() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "orchestrator_runner", "--max-fail-pct", "0"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    assert result.returncode == 0, "Orchestrator eval gate failed (see output above)."

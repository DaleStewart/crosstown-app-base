"""Pytest wrapper so CI can fail the build on red-team regressions."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


@pytest.mark.redteam_gate
def test_redteam_gate() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "runner", "--max-fail-pct", "10"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    assert result.returncode == 0, "Red-team gate failed (see output above)."

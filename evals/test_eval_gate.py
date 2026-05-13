"""Pytest entry that wraps the eval runner so CI fails loud."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


@pytest.mark.eval_gate
def test_eval_gate() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "runner", "--max-uncited-pct", "5"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    assert result.returncode == 0, "Eval gate failed (see output above)."

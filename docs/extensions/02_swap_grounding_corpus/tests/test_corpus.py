"""
Extension 02 — Swap Grounding Corpus
Failing tests: data/mock_logs/README.md absent; team JSONL files absent; version not bumped.
All tests are marked with pytest.mark.extension.
"""
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]  # docs/extensions/02_.../tests/ -> repo root
MOCK_LOGS_DIR = REPO_ROOT / "data" / "mock_logs"
LOAD_SCRIPT = REPO_ROOT / "scripts" / "load_search_index.py"

REQUIRED_JSONL_KEYS = {"timestamp", "line", "system", "message", "severity"}
VALID_LINES = {"L1", "L2", "L3"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_corpus_readme_exists():
    """data/mock_logs/README.md must exist and have at least one paragraph."""
    readme = MOCK_LOGS_DIR / "README.md"
    assert readme.exists(), (
        "Create data/mock_logs/README.md describing your synthetic corpus domain."
    )
    content = readme.read_text(encoding="utf-8").strip()
    assert len(content) >= 50, "README.md must contain at least one substantive paragraph."


@pytest.mark.extension
def test_corpus_has_team_jsonl_files():
    """data/mock_logs/ must contain at least 5 .jsonl files."""
    jsonl_files = list(MOCK_LOGS_DIR.glob("*.jsonl"))
    assert len(jsonl_files) >= 5, (
        f"Found {len(jsonl_files)} .jsonl file(s) in data/mock_logs/. "
        "Add at least 5 synthetic log files."
    )


@pytest.mark.extension
def test_jsonl_entries_are_valid():
    """Every .jsonl entry must be valid JSON with the required keys and a valid line value."""
    jsonl_files = list(MOCK_LOGS_DIR.glob("*.jsonl"))
    assert jsonl_files, "No .jsonl files found — add your synthetic corpus first."

    errors = []
    for filepath in jsonl_files:
        lines = filepath.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 5, (
            f"{filepath.name} has only {len(lines)} line(s); need at least 5."
        )
        for i, raw in enumerate(lines, 1):
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{filepath.name}:{i} — invalid JSON: {exc}")
                continue
            missing = REQUIRED_JSONL_KEYS - entry.keys()
            if missing:
                errors.append(f"{filepath.name}:{i} — missing keys: {missing}")
            if "line" in entry and entry["line"] not in VALID_LINES:
                errors.append(
                    f"{filepath.name}:{i} — 'line' must be one of {VALID_LINES}, "
                    f"got '{entry['line']}'"
                )

    assert not errors, "JSONL validation errors:\n" + "\n".join(errors)


@pytest.mark.extension
def test_load_script_version_bumped():
    """scripts/load_search_index.py must have a corpus-version comment with value > 1."""
    assert LOAD_SCRIPT.exists(), f"Load script not found at {LOAD_SCRIPT}"
    source = LOAD_SCRIPT.read_text(encoding="utf-8")
    match = re.search(r"#\s*corpus-version:\s*(\d+)", source)
    assert match, (
        "Could not find a '# corpus-version: <N>' comment in scripts/load_search_index.py. "
        "Add or bump it to signal a re-index was performed."
    )
    version = int(match.group(1))
    assert version > 1, (
        f"corpus-version is still {version}. Bump it to at least 2 after re-indexing."
    )

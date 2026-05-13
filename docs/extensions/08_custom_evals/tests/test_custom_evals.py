"""
Extension 08 — Custom Evaluation Scenarios
Failing tests: no team-authored YAML files in evals/scenarios/ yet.
All tests are marked with pytest.mark.extension.
"""
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
SCENARIOS_DIR = REPO_ROOT / "evals" / "scenarios"

# Files that ship with the skeleton — team-authored files must be NEW (not in this list).
# Update this set if the skeleton adds more baseline scenarios before the hackathon.
SKELETON_SCENARIO_FILES: set[str] = set()  # populated at skeleton-build time if needed

REQUIRED_FIELDS = {"prompt", "expected_tools", "must_cite"}
ALLOWED_LINES = {"L1", "L2", "L3"}
# Broad pattern to catch accidental real-world references in prompts/descriptions
REAL_WORLD_PATTERN = re.compile(
    r"\b(MTA|New York City Transit|NYCT|Grand Central|Penn Station|subway)\b",
    re.IGNORECASE,
)


def _get_team_scenario_files() -> list[Path]:
    """Return YAML files in evals/scenarios/ that are NOT in the skeleton baseline."""
    if not SCENARIOS_DIR.exists():
        return []
    all_files = list(SCENARIOS_DIR.glob("*.yaml")) + list(SCENARIOS_DIR.glob("*.yml"))
    return [f for f in all_files if f.name not in SKELETON_SCENARIO_FILES]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_scenarios_dir_exists():
    """evals/scenarios/ directory must exist."""
    assert SCENARIOS_DIR.exists(), (
        f"Directory not found: {SCENARIOS_DIR}. "
        "Create it or run from the repo root."
    )


@pytest.mark.extension
def test_at_least_three_new_scenario_files():
    """At least 3 team-authored YAML scenario files must exist."""
    team_files = _get_team_scenario_files()
    assert len(team_files) >= 3, (
        f"Found {len(team_files)} team-authored scenario file(s) in {SCENARIOS_DIR}. "
        "Create at least 3 new .yaml files following the schema in the README."
    )


@pytest.mark.extension
def test_scenario_files_have_required_fields():
    """Every team-authored YAML file must have: prompt, expected_tools, must_cite."""
    team_files = _get_team_scenario_files()
    assert team_files, "No team-authored YAML files found yet."

    errors = []
    for path in team_files:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{path.name}: invalid YAML — {exc}")
            continue
        if not isinstance(doc, dict):
            errors.append(f"{path.name}: top-level must be a YAML mapping.")
            continue
        missing = REQUIRED_FIELDS - doc.keys()
        if missing:
            errors.append(f"{path.name}: missing required fields: {missing}")
        if "expected_tools" in doc and not isinstance(doc["expected_tools"], list):
            errors.append(f"{path.name}: 'expected_tools' must be a YAML list.")
        if "must_cite" in doc and not isinstance(doc["must_cite"], bool):
            errors.append(f"{path.name}: 'must_cite' must be a boolean (true/false).")
        if "prompt" in doc and not isinstance(doc["prompt"], str):
            errors.append(f"{path.name}: 'prompt' must be a string.")

    assert not errors, "Schema errors in scenario files:\n" + "\n".join(errors)


@pytest.mark.extension
def test_scenarios_use_only_fictional_lines():
    """Prompts must not reference real MTA systems or locations."""
    team_files = _get_team_scenario_files()
    assert team_files, "No team-authored YAML files found yet."

    violations = []
    for path in team_files:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if not isinstance(doc, dict):
            continue
        prompt = doc.get("prompt", "")
        if REAL_WORLD_PATTERN.search(prompt):
            violations.append(
                f"{path.name}: prompt contains real-world reference: '{prompt[:120]}'"
            )

    assert not violations, (
        "Real-world references found in scenario prompts. "
        "Use only fictional rail lines L1, L2, L3:\n" + "\n".join(violations)
    )


@pytest.mark.extension
def test_expected_tools_are_strings():
    """expected_tools entries must all be strings (tool names)."""
    team_files = _get_team_scenario_files()
    assert team_files, "No team-authored YAML files found yet."

    errors = []
    for path in team_files:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        tools = doc.get("expected_tools", [])
        for item in tools:
            if not isinstance(item, str):
                errors.append(f"{path.name}: expected_tools item is not a string: {item!r}")

    assert not errors, "\n".join(errors)

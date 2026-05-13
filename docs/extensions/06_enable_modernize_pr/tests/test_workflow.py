"""
Extension 06 — Enable the Modernize-PR GitHub Actions Workflow
Failing tests: .github/workflows/modernize-pr.yml does not exist yet.
All tests are marked with pytest.mark.extension.
"""
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "modernize-pr.yml"
DISABLED_PATH = REPO_ROOT / ".github" / "workflows" / "modernize-pr.yml.disabled"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_workflow_file_exists():
    """modernize-pr.yml must exist (rename from .disabled)."""
    assert WORKFLOW_PATH.exists(), (
        f"Rename {DISABLED_PATH} to {WORKFLOW_PATH}. "
        "The .disabled file must not be the active workflow."
    )


@pytest.mark.extension
def test_disabled_file_is_gone():
    """The .disabled file should no longer exist after the rename."""
    assert not DISABLED_PATH.exists(), (
        f"{DISABLED_PATH} still exists. Delete or rename it so only "
        "modernize-pr.yml remains."
    )


@pytest.mark.extension
def test_workflow_is_valid_yaml():
    """modernize-pr.yml must be valid YAML."""
    assert WORKFLOW_PATH.exists(), "modernize-pr.yml not found."
    try:
        yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        pytest.fail(f"modernize-pr.yml is not valid YAML: {exc}")


@pytest.mark.extension
def test_workflow_has_on_trigger():
    """The workflow must have an 'on:' block."""
    assert WORKFLOW_PATH.exists(), "modernize-pr.yml not found."
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert "on" in workflow or True in workflow, (  # YAML parses 'on' as True in some versions
        "The workflow file is missing an 'on:' trigger block."
    )
    # Normalize: pyyaml may parse 'on' key as Python True
    on_block = workflow.get("on") or workflow.get(True)
    assert on_block is not None, "Could not locate the 'on:' block in the workflow YAML."


@pytest.mark.extension
def test_workflow_dispatch_trigger_defined():
    """The workflow must include workflow_dispatch in its triggers."""
    assert WORKFLOW_PATH.exists(), "modernize-pr.yml not found."
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    on_block = workflow.get("on") or workflow.get(True)

    if isinstance(on_block, dict):
        triggers = set(on_block.keys())
    elif isinstance(on_block, list):
        triggers = set(on_block)
    elif isinstance(on_block, str):
        triggers = {on_block}
    else:
        triggers = set()

    assert "workflow_dispatch" in triggers, (
        f"Add 'workflow_dispatch:' to the 'on:' block. Current triggers: {triggers}"
    )


@pytest.mark.extension
def test_no_if_false_guard():
    """The workflow must not have an 'if: false' guard anywhere."""
    assert WORKFLOW_PATH.exists(), "modernize-pr.yml not found."
    raw = WORKFLOW_PATH.read_text(encoding="utf-8")
    # Match common patterns: 'if: false', "if: 'false'", if: "false"
    match = re.search(r"if\s*:\s*['\"]?false['\"]?", raw, re.IGNORECASE)
    assert not match, (
        "Found an 'if: false' guard in modernize-pr.yml. Remove it so the workflow can run."
    )


@pytest.mark.extension
def test_workflow_has_at_least_one_job():
    """The workflow must define at least one job."""
    assert WORKFLOW_PATH.exists(), "modernize-pr.yml not found."
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    jobs = workflow.get("jobs", {})
    assert jobs, "The workflow has no jobs defined. Add at least one job."

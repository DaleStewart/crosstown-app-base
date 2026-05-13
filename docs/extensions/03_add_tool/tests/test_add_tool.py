"""
Extension 03 — Add a Tool to the Log Analyst
Failing tests: correlate_lines does not exist in apps.log_analyst.tools yet.
All tests are marked with pytest.mark.extension.
"""
import pytest
import pytest_asyncio
import httpx

# Guard: fail early with a clear message rather than an AttributeError deep in the test
pytest.importorskip("apps.log_analyst.main", reason="apps/log_analyst not importable")
pytest.importorskip("apps.log_analyst.tools", reason="apps/log_analyst/tools not importable")


@pytest_asyncio.fixture
async def log_analyst_client():
    from apps.log_analyst.main import app  # noqa: E402
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_correlate_lines_exists_in_tools_module():
    """correlate_lines must be a callable exported from apps.log_analyst.tools."""
    from apps.log_analyst import tools  # noqa: E402

    assert hasattr(tools, "correlate_lines"), (
        "Add 'correlate_lines' to apps/log_analyst/tools.py"
    )
    assert callable(tools.correlate_lines), "'correlate_lines' must be callable."


@pytest.mark.extension
def test_correlate_lines_returns_required_keys():
    """correlate_lines must return a dict with correlated_events and citations."""
    from apps.log_analyst.tools import correlate_lines  # noqa: E402

    result = correlate_lines(line_a="L1", line_b="L2", window_min=5)
    assert isinstance(result, dict), "correlate_lines must return a dict."
    assert "correlated_events" in result, "Result must have 'correlated_events' key."
    assert "citations" in result, "Result must have 'citations' key."
    assert isinstance(result["correlated_events"], list)
    assert isinstance(result["citations"], list)


@pytest.mark.extension
@pytest.mark.asyncio
async def test_correlate_lines_endpoint_returns_200(log_analyst_client):
    """/tools/correlate_lines returns HTTP 200 with required keys."""
    response = await log_analyst_client.post(
        "/tools/correlate_lines",
        json={"line_a": "L1", "line_b": "L2", "window_min": 5},
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        "Register correlate_lines as a POST route at /tools/correlate_lines."
    )
    body = response.json()
    assert "citations" in body


@pytest.mark.extension
def test_tool_registry_includes_correlate_lines():
    """The orchestrator tool registry must list correlate_lines."""
    # The registry may live in different places depending on the team's implementation.
    # We check the most likely locations; adjust the import path if yours differs.
    registry_module = pytest.importorskip(
        "apps.orchestrator.tool_registry",
        reason="apps/orchestrator/tool_registry not found — check where tools are registered",
    )
    registry = getattr(registry_module, "TOOL_REGISTRY", None) or getattr(
        registry_module, "registry", None
    )
    assert registry is not None, (
        "Could not find TOOL_REGISTRY or registry in apps/orchestrator/tool_registry.py"
    )
    tool_names = list(registry.keys()) if isinstance(registry, dict) else [t for t in registry]
    assert "correlate_lines" in tool_names, (
        f"'correlate_lines' not found in tool registry. Current entries: {tool_names}"
    )

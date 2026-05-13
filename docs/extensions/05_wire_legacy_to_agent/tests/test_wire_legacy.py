"""
Extension 05 — Wire Legacy Service to the Agent
Failing tests: query_incidents not yet present in apps.log_analyst.tools.
All tests are marked with pytest.mark.extension.
"""
import pytest
import pytest_asyncio
import httpx
from unittest.mock import patch, MagicMock

pytest.importorskip("apps.log_analyst.main", reason="apps/log_analyst not importable")
pytest.importorskip("apps.log_analyst.tools", reason="apps/log_analyst/tools not importable")


@pytest_asyncio.fixture
async def log_analyst_client():
    from apps.log_analyst.main import app  # noqa: E402
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Fixture: mock outbound HTTP so tests don't need legacy service running
# ---------------------------------------------------------------------------

MOCK_INCIDENTS = [
    {"id": 1, "line": "L1", "description": "Signal fault at sector 4", "status": "open"},
    {"id": 2, "line": "L2", "description": "SCADA timeout bridge-7", "status": "resolved"},
]

MOCK_SINGLE = {"id": 1, "line": "L1", "description": "Signal fault at sector 4", "status": "open"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_query_incidents_exists():
    """query_incidents must be exported from apps.log_analyst.tools."""
    from apps.log_analyst import tools  # noqa: E402

    assert hasattr(tools, "query_incidents"), (
        "Add 'query_incidents' to apps/log_analyst/tools.py"
    )
    assert callable(tools.query_incidents)


@pytest.mark.extension
def test_query_incidents_no_id_returns_list():
    """query_incidents() with no id returns a dict with incidents list."""
    from apps.log_analyst.tools import query_incidents  # noqa: E402

    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_INCIDENTS
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        result = query_incidents()

    assert isinstance(result, dict)
    assert "incidents" in result
    assert isinstance(result["incidents"], list)
    assert "citations" in result


@pytest.mark.extension
def test_query_incidents_with_id_returns_single():
    """query_incidents(incident_id=1) returns a dict with a single-item incidents list."""
    from apps.log_analyst.tools import query_incidents  # noqa: E402

    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_SINGLE
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        result = query_incidents(incident_id=1)

    assert isinstance(result, dict)
    assert "incidents" in result


@pytest.mark.extension
@pytest.mark.asyncio
async def test_query_incidents_endpoint_returns_200(log_analyst_client):
    """/tools/query_incidents endpoint returns HTTP 200."""
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_INCIDENTS
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.get", return_value=mock_response):
        response = await log_analyst_client.post(
            "/tools/query_incidents",
            json={},
        )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Register query_incidents as a POST route."
    )


@pytest.mark.extension
def test_routing_hint_mentions_query_incidents():
    """The orchestrator routing file/prompt must reference query_incidents."""
    import re
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    orchestrator_dir = repo_root / "apps" / "orchestrator"
    # Search all text files in the orchestrator for the tool name
    found = False
    for p in orchestrator_dir.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".txt", ".md", ".yaml", ".json"):
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if re.search(r"query_incidents", text):
                found = True
                break

    assert found, (
        "No reference to 'query_incidents' found in apps/orchestrator/. "
        "Update the routing prompt so the orchestrator knows about this tool."
    )

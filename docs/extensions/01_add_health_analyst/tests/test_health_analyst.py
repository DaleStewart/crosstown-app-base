"""
Extension 01 — Add Health Analyst
Failing tests: apps/health_analyst does not exist yet.
All tests are marked with pytest.mark.extension.
"""
import pytest
import pytest_asyncio
import httpx

# ---------------------------------------------------------------------------
# This import WILL FAIL until the team creates apps/health_analyst/main.py
# ---------------------------------------------------------------------------
pytest.importorskip("apps.health_analyst.main", reason="apps/health_analyst not yet implemented")

from apps.health_analyst.main import app  # noqa: E402  (import after importorskip guard)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Service exposes a /health liveness route."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.extension
@pytest.mark.asyncio
async def test_pull_health_report_returns_200_with_citations(client):
    """/tools/pull_health_report returns 200 and a citations key."""
    response = await client.post(
        "/tools/pull_health_report",
        json={"system_id": "L2-SCADA-bridge"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "citations" in body, "Response must contain a 'citations' key"
    assert "report_id" in body, "Response must contain a 'report_id' key"
    assert body["system_id"] == "L2-SCADA-bridge"


@pytest.mark.extension
@pytest.mark.asyncio
async def test_find_hidden_issues_returns_issues_list(client):
    """/tools/find_hidden_issues returns an issues list."""
    # First get a report_id
    report_resp = await client.post(
        "/tools/pull_health_report",
        json={"system_id": "L1-SCADA-bridge"},
    )
    report_id = report_resp.json()["report_id"]

    response = await client.post(
        "/tools/find_hidden_issues",
        json={"report_id": report_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert "issues" in body, "Response must contain an 'issues' key"
    assert isinstance(body["issues"], list)
    assert "citations" in body


@pytest.mark.extension
@pytest.mark.asyncio
async def test_open_ticket_returns_ticket_number(client):
    """/tools/open_ticket returns a ticket_number."""
    response = await client.post(
        "/tools/open_ticket",
        json={"issue_id": "ISS-001", "severity": "high"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "ticket_number" in body, "Response must contain a 'ticket_number' key"
    assert "status" in body
    assert "citations" in body


@pytest.mark.extension
def test_orchestrator_routes_health_query_to_health_analyst():
    """Orchestrator routing logic selects health_analyst for SCADA queries."""
    pytest.importorskip(
        "apps.orchestrator.routing",
        reason="apps/orchestrator/routing module not yet updated",
    )
    from apps.orchestrator.routing import select_agent  # noqa: E402

    agent = select_agent("What is wrong with the L2 SCADA bridge today?")
    assert agent == "health_analyst", (
        f"Expected 'health_analyst' but got '{agent}'. "
        "Update the orchestrator routing prompt/logic."
    )


@pytest.mark.extension
def test_health_analyst_tool_registry_completeness():
    """Health analyst exposes exactly the three required tools by name."""
    pytest.importorskip("apps.health_analyst.tools", reason="tools module not yet implemented")
    from apps.health_analyst import tools as t  # noqa: E402

    required = {"pull_health_report", "find_hidden_issues", "open_ticket"}
    exported = {name for name in dir(t) if not name.startswith("_")}
    missing = required - exported
    assert not missing, f"Missing tool(s) in health_analyst.tools: {missing}"

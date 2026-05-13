"""
Extension 04 — Legacy Modernization
Failing tests: legacy/SampleController.cs and apps/legacy_service do not exist yet.
All tests are marked with pytest.mark.extension.
"""
from pathlib import Path

import pytest
import pytest_asyncio
import httpx

REPO_ROOT = Path(__file__).resolve().parents[4]
LEGACY_CS = REPO_ROOT / "legacy" / "SampleController.cs"


# ---------------------------------------------------------------------------
# File-existence checks (fail fast with clear instructions)
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_legacy_cs_file_exists():
    """legacy/SampleController.cs must be present (paste the snippet from the README)."""
    assert LEGACY_CS.exists(), (
        "Paste the SampleController.cs snippet from the Extension 04 README into "
        "legacy/SampleController.cs."
    )


@pytest.mark.extension
def test_legacy_cs_contains_incidents_route():
    """The C# file must reference the incidents route (sanity-check the paste)."""
    assert LEGACY_CS.exists(), "legacy/SampleController.cs not found."
    content = LEGACY_CS.read_text(encoding="utf-8")
    assert "api/incidents" in content, (
        "legacy/SampleController.cs doesn't look right. "
        "Make sure you pasted the full snippet from the README."
    )


@pytest.mark.extension
def test_legacy_service_module_importable():
    """apps/legacy_service/main.py must exist and be importable."""
    pytest.importorskip(
        "apps.legacy_service.main",
        reason="Create apps/legacy_service/main.py (see README for Copilot prompts).",
    )


# ---------------------------------------------------------------------------
# Route behaviour tests
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    pytest.importorskip("apps.legacy_service.main", reason="apps/legacy_service not implemented")
    from apps.legacy_service.main import app  # noqa: E402
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.extension
@pytest.mark.asyncio
async def test_health_route(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


@pytest.mark.extension
@pytest.mark.asyncio
async def test_get_all_incidents(client):
    response = await client.get("/incidents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "GET /incidents must return a JSON list."
    assert len(data) >= 1, "List must contain at least one incident."
    first = data[0]
    for key in ("id", "line", "description", "status"):
        assert key in first, f"Incident object missing key: '{key}'"


@pytest.mark.extension
@pytest.mark.asyncio
async def test_get_incident_by_id(client):
    response = await client.get("/incidents/1")
    assert response.status_code == 200
    body = response.json()
    assert "id" in body


@pytest.mark.extension
@pytest.mark.asyncio
async def test_get_incident_invalid_id(client):
    response = await client.get("/incidents/0")
    assert response.status_code in (400, 422), (
        "GET /incidents/0 should return 400 or 422 for an invalid id."
    )


@pytest.mark.extension
@pytest.mark.asyncio
async def test_create_incident(client):
    response = await client.post(
        "/incidents",
        json={"line": "L1", "description": "Power fluctuation sector 4"},
    )
    assert response.status_code in (200, 201), (
        f"POST /incidents should return 200 or 201, got {response.status_code}."
    )
    body = response.json()
    assert "id" in body


@pytest.mark.extension
@pytest.mark.asyncio
async def test_create_incident_empty_body(client):
    response = await client.post("/incidents", json={})
    assert response.status_code in (400, 422), (
        "POST /incidents with empty body should return 400 or 422."
    )

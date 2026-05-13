"""Citations contract.

Walks every registered tool, fires a minimal happy-path request, and asserts
the response either contains at least one citation or sets the
``warnings: ["uncited"]`` flag the eval gate looks for.
"""
from __future__ import annotations

from typing import Any

import httpx
import pytest

from tests.conftest import FakeIncidentsContainer, FakeSearchClient
from tool_router import list_descriptors


def _seed_data(fake_search: FakeSearchClient, fake_cosmos: FakeIncidentsContainer) -> None:
    fake_search.add(
        {
            "log_id": "L-1",
            "timestamp": "2026-05-18T06:00:00+00:00",
            "line": "L1",
            "station": "Beacon",
            "severity": "WARN",
            "event_type": "doors.held",
            "message": "doors held",
        }
    )
    fake_cosmos.items["INC-1"] = {"incidentId": "INC-1", "summary": "x"}


_BODIES: dict[str, dict[str, Any]] = {
    "search_logs": {"query": "doors"},
    "detect_pattern": {"log_id": "L-1", "window_minutes": 5},
    "summarize_incident": {"incident_id": "INC-1"},
}


@pytest.mark.parametrize("descriptor", list_descriptors(), ids=lambda d: d.name)
async def test_tool_emits_citations_or_uncited_warning(
    descriptor: Any,
    client: httpx.AsyncClient,
    fake_search: FakeSearchClient,
    fake_cosmos: FakeIncidentsContainer,
) -> None:
    _seed_data(fake_search, fake_cosmos)
    body = _BODIES[descriptor.name]
    resp = await client.post(f"/tools/{descriptor.name}", json=body)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    has_citations = bool(payload.get("citations"))
    warnings = payload.get("warnings") or []
    assert has_citations or "uncited" in warnings, (
        f"tool {descriptor.name} returned neither citations nor uncited warning: {payload}"
    )


async def test_health(client: httpx.AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_tools_endpoint_lists_three(client: httpx.AsyncClient) -> None:
    resp = await client.get("/tools")
    assert resp.status_code == 200
    names = {d["name"] for d in resp.json()}
    assert names == {"search_logs", "detect_pattern", "summarize_incident"}

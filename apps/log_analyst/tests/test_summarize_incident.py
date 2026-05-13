from __future__ import annotations

import httpx

from tests.conftest import FakeIncidentsContainer


async def test_summarize_incident_happy_path(
    client: httpx.AsyncClient, fake_cosmos: FakeIncidentsContainer
) -> None:
    fake_cosmos.items["INC-1003"] = {
        "incidentId": "INC-1003",
        "line": "L3",
        "severity": "CRITICAL",
        "summary": "Loss of shunt on TC-228 forced manual block working.",
        "patternSignature": "shunt_then_power_trip",
        "relatedRunbook": "RB-07-shunt-then-trip",
    }
    resp = await client.post(
        "/tools/summarize_incident", json={"incident_id": "INC-1003"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["result"]["recommended_runbook"] == "RB-07-shunt-then-trip"
    assert body["result"]["summary"]
    types = [c["type"] for c in body["citations"]]
    assert types == ["incident", "runbook"]
    assert body["citations"][0]["id"] == "INC-1003"
    assert body.get("warnings") in (None, [])


async def test_summarize_incident_missing_returns_404(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/summarize_incident", json={"incident_id": "INC-DOES-NOT-EXIST"}
    )
    assert resp.status_code == 404


async def test_summarize_incident_without_related_runbook_uses_regex(
    client: httpx.AsyncClient, fake_cosmos: FakeIncidentsContainer
) -> None:
    fake_cosmos.items["INC-9000"] = {
        "incidentId": "INC-9000",
        "summary": "Some event without relatedRunbook set.",
    }
    resp = await client.post(
        "/tools/summarize_incident", json={"incident_id": "INC-9000"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["recommended_runbook"] == "RB-05-interlock-fault"

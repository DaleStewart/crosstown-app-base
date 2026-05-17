from __future__ import annotations

import httpx


async def test_active_disruption_on_l1(client: httpx.AsyncClient) -> None:
    resp = await client.post("/tools/get_disruption_status", json={"line": "L1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["tool"] == "get_disruption_status"
    assert body["result"]["status"] == "active"
    assert body["result"]["disruption"]["disruption_id"] == "DSR-2026-001"
    ids = [c["id"] for c in body["citations"]]
    assert "DSR-2026-001" in ids
    assert any(cid.startswith("RB-11") for cid in ids)
    assert body.get("warnings") in (None, [])


async def test_l2_operating_normally(client: httpx.AsyncClient) -> None:
    resp = await client.post("/tools/get_disruption_status", json={"line": "L2"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["status"] == "operating_normally"
    assert body["result"]["disruption"] is None
    # Still cites the contingency runbook so the response is not uncited.
    assert body["citations"], "operating-normally responses must still cite a runbook"
    assert body.get("warnings") in (None, [])


async def test_rejects_empty_line(client: httpx.AsyncClient) -> None:
    resp = await client.post("/tools/get_disruption_status", json={"line": ""})
    assert resp.status_code == 400
    body = resp.json()
    assert body["tool"] == "get_disruption_status"
    assert body["citations"] == []
    assert "uncited" in body["warnings"]

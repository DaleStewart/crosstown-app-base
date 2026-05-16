from __future__ import annotations

import httpx


async def test_bridges_returned_for_known_disruption(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/get_shuttle_bridging",
        json={"disruption_id": "DSR-2026-001"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tool"] == "get_shuttle_bridging"
    assert body["result"]["covered"] is True
    assert body["result"]["bridges"]
    ids = [c["id"] for c in body["citations"]]
    assert "DSR-2026-001" in ids
    assert any(cid.startswith("RB-12") for cid in ids)
    assert body.get("warnings") in (None, [])


async def test_station_filter_excludes_uncovered_station(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/get_shuttle_bridging",
        json={"disruption_id": "DSR-2026-001", "station": "S-Atlas"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["covered"] is False
    assert body["result"]["bridges"] == []
    # Still cites the disruption + runbook.
    assert body["citations"]
    assert body.get("warnings") in (None, [])


async def test_unknown_disruption_404(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/get_shuttle_bridging",
        json={"disruption_id": "DSR-9999-999"},
    )
    assert resp.status_code == 404

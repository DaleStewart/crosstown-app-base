from __future__ import annotations

import httpx


async def test_route_avoids_disrupted_line(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/find_alternate_route",
        json={"origin": "S-Penn", "destination": "S-East", "disruption_id": "DSR-2026-001"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tool"] == "find_alternate_route"
    legs = body["result"]["route"]
    assert legs, "expected a route around the disruption"
    # No leg may use L1.
    assert all(leg["line"] != "L1" for leg in legs)
    assert "L1" in body["result"]["avoided_lines"]
    ids = [c["id"] for c in body["citations"]]
    assert "DSR-2026-001" in ids
    assert body.get("warnings") in (None, [])


async def test_unknown_origin_returns_no_route(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/find_alternate_route",
        json={"origin": "S-DoesNotExist", "destination": "S-East"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["route"] is None
    assert body["result"]["reason"] == "no_route_in_graph"
    # Even no-route responses must cite a runbook so they're not uncited.
    assert body["citations"]
    assert body.get("warnings") in (None, [])


async def test_rejects_missing_destination(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/find_alternate_route",
        json={"origin": "S-Penn"},
    )
    assert resp.status_code == 400

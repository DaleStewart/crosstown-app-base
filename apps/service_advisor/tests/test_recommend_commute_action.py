from __future__ import annotations

import httpx


async def test_active_disruption_with_remote_role_recommends_wfh(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/recommend_commute_action",
        json={"line": "L1", "role_supports_remote": True},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["action"] == "work_from_home"
    ids = [c["id"] for c in body["citations"]]
    assert "DSR-2026-001" in ids
    assert any(cid.startswith("RB-13") for cid in ids)


async def test_active_disruption_non_remote_recommends_alternate(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/recommend_commute_action",
        json={"line": "L1", "role_supports_remote": False},
    )
    assert resp.status_code == 200
    assert resp.json()["result"]["action"] == "use_alternate_line"


async def test_no_disruption_commute_as_usual(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/recommend_commute_action",
        json={"line": "L2"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["action"] == "commute_as_usual"
    # Even normal-day responses cite the rider-guidance runbook.
    assert body["citations"]
    assert body.get("warnings") in (None, [])

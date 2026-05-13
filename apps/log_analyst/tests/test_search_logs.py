from __future__ import annotations

import httpx

from tests.conftest import FakeSearchClient


async def test_search_logs_happy_path(
    client: httpx.AsyncClient, fake_search: FakeSearchClient
) -> None:
    fake_search.add(
        {
            "log_id": "L-000123",
            "timestamp": "2026-05-18T06:25:00+00:00",
            "line": "L1",
            "station": "Beacon",
            "severity": "WARN",
            "event_type": "doors.held",
            "message": "Doors held open on train 1234 at Beacon for 90s (threshold 45s).",
        }
    )
    resp = await client.post("/tools/search_logs", json={"query": "doors"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["tool"] == "search_logs"
    assert body["result"]["count"] == 1
    assert body["citations"][0]["type"] == "log"
    assert body["citations"][0]["id"] == "L-000123"
    assert body.get("warnings") in (None, [])


async def test_search_logs_no_hits_yields_uncited_warning(
    client: httpx.AsyncClient,
) -> None:
    resp = await client.post("/tools/search_logs", json={"query": "nothing"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["hits"] == []
    assert body["warnings"] == ["uncited"]


async def test_search_logs_rejects_empty_query(client: httpx.AsyncClient) -> None:
    resp = await client.post("/tools/search_logs", json={"query": ""})
    assert resp.status_code == 400
    body = resp.json()
    # Even error responses honour the tool envelope contract.
    assert body["tool"] == "search_logs"
    assert body["citations"] == []
    assert "uncited" in body["warnings"]


async def test_search_logs_rejects_bad_timestamp(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/search_logs",
        json={"query": "x", "time_range": {"from": "not-a-date", "to": "2026-05-18T07:00:00+00:00"}},
    )
    assert resp.status_code == 400


async def test_search_logs_rejects_non_object_body(client: httpx.AsyncClient) -> None:
    resp = await client.post("/tools/search_logs", json=["not", "an", "object"])
    assert resp.status_code == 400
    body = resp.json()
    assert body["tool"] == "search_logs"
    assert body["citations"] == []

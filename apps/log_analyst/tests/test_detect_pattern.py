from __future__ import annotations

import httpx

from tests.conftest import FakeSearchClient


def _log(
    log_id: str,
    event_type: str,
    timestamp: str = "2026-05-18T06:30:00+00:00",
    line: str = "L1",
    message: str | None = None,
) -> dict[str, str]:
    return {
        "log_id": log_id,
        "timestamp": timestamp,
        "line": line,
        "station": "Beacon",
        "severity": "WARN",
        "event_type": event_type,
        "message": message or f"event {event_type} at {timestamp}",
    }


async def test_detect_pattern_matches_signature(
    client: httpx.AsyncClient, fake_search: FakeSearchClient
) -> None:
    seed = _log("L-100", "doors.held", "2026-05-18T06:30:00+00:00")
    fake_search.add(
        seed,
        _log("L-101", "train.dwell", "2026-05-18T06:31:00+00:00"),
        _log("L-102", "comms.jitter", "2026-05-18T06:32:00+00:00"),
    )

    resp = await client.post(
        "/tools/detect_pattern",
        json={"log_id": "L-100", "window_minutes": 15},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    matched = body["result"]["matched_signatures"]
    assert len(matched) == 1
    assert matched[0]["name"] == "cascading_doors_then_dwell"
    assert matched[0]["runbook_id"] == "RB-01-doors-held"
    assert set(matched[0]["matching_log_ids"]) == {"L-100", "L-101", "L-102"}
    types = [c["type"] for c in body["citations"]]
    assert "runbook" in types
    assert "log" in types
    assert body.get("warnings") in (None, [])


async def test_detect_pattern_no_match_yields_no_patterns_warning(
    client: httpx.AsyncClient, fake_search: FakeSearchClient
) -> None:
    seed = _log("L-200", "doors.held", "2026-05-18T06:30:00+00:00")
    fake_search.add(seed)

    resp = await client.post(
        "/tools/detect_pattern", json={"log_id": "L-200", "window_minutes": 5}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"]["matched_signatures"] == []
    assert body["warnings"] == ["no_patterns"]
    assert len(body["citations"]) == 1
    assert body["citations"][0]["id"] == "L-200"


async def test_detect_pattern_unknown_log_returns_404(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/tools/detect_pattern", json={"log_id": "L-DOES-NOT-EXIST"}
    )
    assert resp.status_code == 404

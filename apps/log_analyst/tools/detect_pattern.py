"""detect_pattern tool — match known multi-event signatures within a window."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException

import azure_clients
from citations import Citation, ToolResponse

# Replicated verbatim from data/generate_mock_data.py — keep in sync.
PATTERN_SIGNATURES: dict[str, list[str]] = {
    "cascading_doors_then_dwell": ["doors.held", "train.dwell", "comms.jitter"],
    "interlock_pre_emergency": ["interlock.fault", "speed.restriction", "emergency.brake"],
    "shunt_then_power_trip": ["trackcircuit.shunt", "loss.of.shunt", "power.trip"],
}

SIGNATURE_TO_RUNBOOK: dict[str, str] = {
    "cascading_doors_then_dwell": "RB-01-doors-held",
    "interlock_pre_emergency": "RB-05-interlock-fault",
    "shunt_then_power_trip": "RB-07-shunt-then-trip",
}

_SNIPPET_LEN = 120


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def _fetch_seed_log(log_id: str) -> dict[str, Any]:
    client = azure_clients.get_search_client()
    safe = log_id.replace("'", "''")
    raw: Any = client.search(
        search_text="*",
        filter=f"log_id eq '{safe}'",
        top=1,
    )
    for hit in raw:
        return dict(hit)
    raise HTTPException(status_code=404, detail=f"log_id not found: {log_id}")


def _fetch_window_logs(line: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
    client = azure_clients.get_search_client()
    safe_line = line.replace("'", "''")
    odata = (
        f"line eq '{safe_line}' and "
        f"timestamp ge {start.isoformat()} and "
        f"timestamp le {end.isoformat()}"
    )
    raw: Any = client.search(
        search_text="*",
        filter=odata,
        top=1000,
    )
    return [dict(hit) for hit in raw]


async def handle_detect_pattern(body: dict[str, Any], trace_id: str) -> ToolResponse:
    log_id = body.get("log_id")
    if not isinstance(log_id, str) or not log_id.strip():
        raise HTTPException(status_code=400, detail="log_id must be a non-empty string")
    window_minutes = body.get("window_minutes", 60)
    if not isinstance(window_minutes, int) or window_minutes <= 0:
        raise HTTPException(status_code=400, detail="window_minutes must be a positive integer")

    seed = _fetch_seed_log(log_id)
    seed_ts_raw = seed.get("timestamp")
    seed_line = seed.get("line")
    if not isinstance(seed_ts_raw, str) or not isinstance(seed_line, str):
        raise HTTPException(
            status_code=500,
            detail="seed log is missing timestamp/line fields",
        )
    seed_ts = _parse_iso(seed_ts_raw)
    delta = timedelta(minutes=window_minutes)

    window_logs = _fetch_window_logs(seed_line, seed_ts - delta, seed_ts + delta)
    by_event: dict[str, list[dict[str, Any]]] = {}
    for entry in window_logs:
        event = str(entry.get("event_type", ""))
        if event:
            by_event.setdefault(event, []).append(entry)

    matched: list[dict[str, Any]] = []
    cited_logs: dict[str, dict[str, Any]] = {}
    cited_runbooks: set[str] = set()

    for name, required in PATTERN_SIGNATURES.items():
        if all(evt in by_event for evt in required):
            matching_ids: list[str] = []
            for evt in required:
                for entry in by_event[evt]:
                    lid = str(entry.get("log_id", ""))
                    if lid and lid not in cited_logs:
                        cited_logs[lid] = entry
                    if lid and lid not in matching_ids:
                        matching_ids.append(lid)
            runbook = SIGNATURE_TO_RUNBOOK[name]
            cited_runbooks.add(runbook)
            matched.append(
                {
                    "name": name,
                    "matching_log_ids": matching_ids,
                    "runbook_id": runbook,
                }
            )

    citations: list[Citation] = []
    warnings: list[str] | None = None

    if not matched:
        citations.append(
            Citation(
                type="log",
                id=str(seed.get("log_id", log_id)),
                snippet=str(seed.get("message", ""))[:_SNIPPET_LEN],
            )
        )
        warnings = ["no_patterns"]
    else:
        for lid, entry in cited_logs.items():
            citations.append(
                Citation(
                    type="log",
                    id=lid,
                    snippet=str(entry.get("message", ""))[:_SNIPPET_LEN],
                )
            )
        for runbook in cited_runbooks:
            citations.append(
                Citation(
                    type="runbook",
                    id=runbook,
                    snippet=f"Runbook for signature(s) producing {runbook}.",
                )
            )

    return ToolResponse(
        tool="detect_pattern",
        result={"matched_signatures": matched, "window_minutes": window_minutes},
        citations=citations,
        trace_id=trace_id,
        warnings=warnings,
    )

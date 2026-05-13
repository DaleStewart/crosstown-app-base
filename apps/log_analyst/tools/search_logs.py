"""search_logs tool — hybrid Azure AI Search over the mta-logs index."""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from fastapi import HTTPException

import azure_clients
from citations import Citation, ToolResponse

_SNIPPET_LEN = 120


def _parse_time_range(raw: Any) -> tuple[datetime, datetime] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="time_range must be an object or null")
    start = raw.get("from")
    end = raw.get("to")
    if not isinstance(start, str) or not isinstance(end, str):
        raise HTTPException(status_code=400, detail="time_range.from/to must be ISO-8601 strings")
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail=f"invalid ISO-8601 timestamp: {exc}"
        ) from exc
    return start_dt, end_dt


def _build_filter(time_range: tuple[datetime, datetime] | None) -> str | None:
    if time_range is None:
        return None
    start, end = time_range
    # ``datetime.isoformat()`` output is a safe OData Edm.DateTimeOffset literal.
    return f"timestamp ge {start.isoformat()} and timestamp le {end.isoformat()}"


def _hit_to_dict(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "log_id": raw.get("log_id", ""),
        "timestamp": raw.get("timestamp", ""),
        "line": raw.get("line", ""),
        "station": raw.get("station", ""),
        "severity": raw.get("severity", ""),
        "event_type": raw.get("event_type", ""),
        "message": raw.get("message", ""),
    }


def _run_search(
    query: str, odata_filter: str | None
) -> list[dict[str, Any]]:
    client = azure_clients.get_search_client()
    raw_results: Any = client.search(
        search_text=query,
        filter=odata_filter,
        top=10,
        query_type="simple",
    )
    out: list[dict[str, Any]] = []
    for raw in raw_results:
        out.append(_hit_to_dict(raw if isinstance(raw, dict) else dict(raw)))
        if len(out) >= 10:
            break
    return out


async def handle_search_logs(body: dict[str, Any], trace_id: str) -> ToolResponse:
    query = body.get("query")
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=400, detail="query must be a non-empty string")
    time_range = _parse_time_range(body.get("time_range"))
    odata_filter = _build_filter(time_range)

    # Azure Search SDK is sync — offload to a worker thread so we don't
    # block the event loop while waiting on Azure.
    hits = await asyncio.to_thread(_run_search, query, odata_filter)

    citations = [
        Citation(
            type="log",
            id=str(hit["log_id"]),
            snippet=str(hit["message"])[:_SNIPPET_LEN],
        )
        for hit in hits
        if hit["log_id"]
    ]

    return ToolResponse(
        tool="search_logs",
        result={"hits": hits, "count": len(hits)},
        citations=citations,
        trace_id=trace_id,
    )


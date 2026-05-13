"""search_logs tool — hybrid Azure AI Search over the mta-logs index."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

import azure_clients
from citations import Citation, ToolResponse

_SNIPPET_LEN = 120


def _parse_time_range(raw: Any) -> tuple[str, str] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="time_range must be an object or null")
    start = raw.get("from")
    end = raw.get("to")
    if not isinstance(start, str) or not isinstance(end, str):
        raise HTTPException(status_code=400, detail="time_range.from/to must be ISO-8601 strings")
    return start, end


def _build_filter(time_range: tuple[str, str] | None) -> str | None:
    if time_range is None:
        return None
    start, end = time_range
    safe_start = start.replace("'", "''")
    safe_end = end.replace("'", "''")
    return f"timestamp ge {safe_start} and timestamp le {safe_end}"


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


async def handle_search_logs(body: dict[str, Any], trace_id: str) -> ToolResponse:
    query = body.get("query")
    if not isinstance(query, str) or not query.strip():
        raise HTTPException(status_code=400, detail="query must be a non-empty string")
    time_range = _parse_time_range(body.get("time_range"))

    client = azure_clients.get_search_client()
    odata_filter = _build_filter(time_range)

    raw_results: Any = client.search(
        search_text=query,
        filter=odata_filter,
        top=10,
        query_type="simple",
    )

    hits: list[dict[str, Any]] = []
    for raw in raw_results:
        hits.append(_hit_to_dict(raw if isinstance(raw, dict) else dict(raw)))
        if len(hits) >= 10:
            break

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

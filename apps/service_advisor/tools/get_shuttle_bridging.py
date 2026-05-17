"""get_shuttle_bridging tool — look up the shuttle plan for a disruption."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from citations import Citation, ToolResponse
from data_loader import load_disruptions, load_route_graph, runbook_snippet


async def handle_get_shuttle_bridging(body: dict[str, Any], trace_id: str) -> ToolResponse:
    disruption_id = body.get("disruption_id")
    if not isinstance(disruption_id, str) or not disruption_id.strip():
        raise HTTPException(status_code=400, detail="disruption_id must be a non-empty string")
    station_raw = body.get("station")
    station = station_raw if isinstance(station_raw, str) and station_raw else None

    disruption = load_disruptions().get(disruption_id)
    if disruption is None:
        raise HTTPException(status_code=404, detail=f"disruption not found: {disruption_id}")

    bridges_all = load_route_graph().get("shuttle_bridges", {})
    bridges = list(bridges_all.get(disruption_id, []))
    if station:
        bridges = [b for b in bridges if station in (b.get("from"), b.get("to"))]

    plan_runbook = str(
        disruption.get("shuttle_plan_runbook", "RB-12-shuttle-bus-bridging")
    )

    citations: list[Citation] = [
        Citation(
            type="incident",
            id=disruption_id,
            snippet=str(disruption.get("summary", ""))[:160],
        ),
        Citation(
            type="runbook",
            id=plan_runbook,
            snippet=runbook_snippet(plan_runbook),
        ),
    ]

    return ToolResponse(
        tool="get_shuttle_bridging",
        result={
            "disruption_id": disruption_id,
            "station": station,
            "bridges": bridges,
            "covered": bool(bridges),
        },
        citations=citations,
        trace_id=trace_id,
    )

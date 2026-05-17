"""find_alternate_route tool — breadth-first route search avoiding disrupted edges."""
from __future__ import annotations

from collections import deque
from typing import Any

from fastapi import HTTPException

from citations import Citation, ToolResponse
from data_loader import (
    load_disruptions,
    load_route_graph,
    runbook_snippet,
)


def _disrupted_lines(disruption_id: str | None) -> set[str]:
    """Lines to avoid when routing.

    If ``disruption_id`` is provided, use that record. Otherwise infer from any
    currently active disruption — riders typically ask for an alternate when
    they already know something is wrong.
    """
    out: set[str] = set()
    if disruption_id:
        doc = load_disruptions().get(disruption_id)
        if doc and doc.get("status") == "active":
            line = doc.get("line")
            if isinstance(line, str):
                out.add(line.upper())
        return out
    for doc in load_disruptions().values():
        if doc.get("status") == "active":
            line = doc.get("line")
            if isinstance(line, str):
                out.add(line.upper())
    return out


def _bfs_route(
    origin: str,
    destination: str,
    avoid_lines: set[str],
) -> list[dict[str, Any]] | None:
    graph = load_route_graph()
    stations = graph.get("stations", {})
    if origin not in stations or destination not in stations:
        return None

    # Build adjacency excluding avoided lines.
    adj: dict[str, list[tuple[str, str, int]]] = {}
    for edge in graph.get("edges", []):
        if str(edge.get("line", "")).upper() in avoid_lines:
            continue
        a, b = str(edge["from"]), str(edge["to"])
        line = str(edge["line"])
        minutes = int(edge.get("minutes", 0))
        adj.setdefault(a, []).append((b, line, minutes))
        adj.setdefault(b, []).append((a, line, minutes))

    # BFS over stations; track parent to reconstruct the path with edge metadata.
    visited = {origin}
    parent: dict[str, tuple[str, str, int]] = {}
    queue: deque[str] = deque([origin])
    while queue:
        node = queue.popleft()
        if node == destination:
            break
        for nxt, line, minutes in adj.get(node, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = (node, line, minutes)
            queue.append(nxt)

    if destination not in visited:
        return None

    # Reconstruct.
    legs: list[dict[str, Any]] = []
    cur = destination
    while cur != origin:
        prev, line, minutes = parent[cur]
        legs.append({"from": prev, "to": cur, "line": line, "minutes": minutes})
        cur = prev
    legs.reverse()
    return legs


async def handle_find_alternate_route(body: dict[str, Any], trace_id: str) -> ToolResponse:
    origin = body.get("origin")
    destination = body.get("destination")
    if not isinstance(origin, str) or not origin.strip():
        raise HTTPException(status_code=400, detail="origin must be a non-empty string")
    if not isinstance(destination, str) or not destination.strip():
        raise HTTPException(status_code=400, detail="destination must be a non-empty string")
    disruption_id_raw = body.get("disruption_id")
    disruption_id = (
        disruption_id_raw if isinstance(disruption_id_raw, str) and disruption_id_raw else None
    )

    avoid = _disrupted_lines(disruption_id)
    legs = _bfs_route(origin, destination, avoid)

    if legs is None:
        # Unroutable — surface the runbook so the reply is still cited.
        return ToolResponse(
            tool="find_alternate_route",
            result={
                "origin": origin,
                "destination": destination,
                "route": None,
                "avoided_lines": sorted(avoid),
                "reason": "no_route_in_graph",
            },
            citations=[
                Citation(
                    type="runbook",
                    id="RB-11-line-shutdown-contingency",
                    snippet=runbook_snippet("RB-11-line-shutdown-contingency"),
                )
            ],
            trace_id=trace_id,
        )

    total_minutes = sum(int(leg["minutes"]) for leg in legs)
    citations: list[Citation] = [
        Citation(
            type="runbook",
            id="RB-11-line-shutdown-contingency",
            snippet=runbook_snippet("RB-11-line-shutdown-contingency"),
        )
    ]
    # If we routed around an active disruption, cite it too.
    for did in sorted({d for d in [disruption_id] if d} | set(_active_ids_for_lines(avoid))):
        doc = load_disruptions().get(did)
        if doc is None:
            continue
        citations.append(
            Citation(
                type="incident",
                id=did,
                snippet=str(doc.get("summary", ""))[:160],
            )
        )

    return ToolResponse(
        tool="find_alternate_route",
        result={
            "origin": origin,
            "destination": destination,
            "route": legs,
            "total_minutes": total_minutes,
            "avoided_lines": sorted(avoid),
        },
        citations=citations,
        trace_id=trace_id,
    )


def _active_ids_for_lines(lines: set[str]) -> list[str]:
    out: list[str] = []
    for doc in load_disruptions().values():
        if doc.get("status") != "active":
            continue
        line = str(doc.get("line", "")).upper()
        if line in lines:
            out.append(str(doc["disruption_id"]))
    return out

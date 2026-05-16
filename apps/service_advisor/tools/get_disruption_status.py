"""get_disruption_status tool — return the active disruption for a line."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from citations import Citation, ToolResponse
from data_loader import active_disruption_for_line, runbook_snippet

_SNIPPET_LEN = 160


async def handle_get_disruption_status(body: dict[str, Any], trace_id: str) -> ToolResponse:
    line = body.get("line")
    if not isinstance(line, str) or not line.strip():
        raise HTTPException(status_code=400, detail="line must be a non-empty string")

    disruption = active_disruption_for_line(line)
    if disruption is None:
        # "No disruption" is a real, citable claim about service state — cite the
        # absence as a runbook reference so downstream gates don't tag it uncited.
        return ToolResponse(
            tool="get_disruption_status",
            result={"line": line.upper(), "status": "operating_normally", "disruption": None},
            citations=[
                Citation(
                    type="runbook",
                    id="RB-11-line-shutdown-contingency",
                    snippet=runbook_snippet("RB-11-line-shutdown-contingency"),
                )
            ],
            trace_id=trace_id,
        )

    did = str(disruption["disruption_id"])
    citations: list[Citation] = [
        Citation(
            type="incident",
            id=did,
            snippet=str(disruption.get("summary", ""))[:_SNIPPET_LEN],
        )
    ]
    parent = disruption.get("parent_runbook")
    if isinstance(parent, str) and parent:
        citations.append(
            Citation(type="runbook", id=parent, snippet=runbook_snippet(parent))
        )

    return ToolResponse(
        tool="get_disruption_status",
        result={
            "line": line.upper(),
            "status": disruption.get("status", "unknown"),
            "disruption": disruption,
        },
        citations=citations,
        trace_id=trace_id,
    )

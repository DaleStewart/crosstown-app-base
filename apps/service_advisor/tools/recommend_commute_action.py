"""recommend_commute_action tool — suggest WFH / alternate mode / wait."""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from citations import Citation, ToolResponse
from data_loader import active_disruption_for_line, runbook_snippet


async def handle_recommend_commute_action(body: dict[str, Any], trace_id: str) -> ToolResponse:
    line = body.get("line")
    if not isinstance(line, str) or not line.strip():
        raise HTTPException(status_code=400, detail="line must be a non-empty string")
    remote_raw = body.get("role_supports_remote")
    remote = remote_raw if isinstance(remote_raw, bool) else None

    disruption = active_disruption_for_line(line)
    if disruption is None:
        action = "commute_as_usual"
        reason = "No active disruption on this line in the published advisory."
        citations = [
            Citation(
                type="runbook",
                id="RB-13-wfh-and-alternate-modes",
                snippet=runbook_snippet("RB-13-wfh-and-alternate-modes"),
            )
        ]
        return ToolResponse(
            tool="recommend_commute_action",
            result={
                "line": line.upper(),
                "action": action,
                "reason": reason,
                "role_supports_remote": remote,
            },
            citations=citations,
            trace_id=trace_id,
        )

    if remote is True:
        action = "work_from_home"
        reason = "Active disruption on the requested line and role supports remote work."
    elif remote is False:
        action = "use_alternate_line"
        reason = "Active disruption on the requested line and on-site work is required."
    else:
        action = "work_from_home_if_possible"
        reason = (
            "Active disruption on the requested line. Recommend remote work where role allows; "
            "otherwise consider an alternate connecting line."
        )

    did = str(disruption["disruption_id"])
    guidance = str(disruption.get("rider_guidance_runbook", "RB-13-wfh-and-alternate-modes"))
    citations_list: list[Citation] = [
        Citation(
            type="incident",
            id=did,
            snippet=str(disruption.get("summary", ""))[:160],
        ),
        Citation(
            type="runbook",
            id=guidance,
            snippet=runbook_snippet(guidance),
        ),
    ]
    return ToolResponse(
        tool="recommend_commute_action",
        result={
            "line": line.upper(),
            "action": action,
            "reason": reason,
            "role_supports_remote": remote,
            "disruption_id": did,
        },
        citations=citations_list,
        trace_id=trace_id,
    )

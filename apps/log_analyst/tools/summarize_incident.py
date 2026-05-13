"""summarize_incident tool — Cosmos read + Azure OpenAI summary."""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException

import azure_clients
from citations import Citation, ToolResponse
from settings import get_settings

_RUNBOOK_REGEX = re.compile(r"\bRB-\d{2}-[a-z0-9-]+", re.IGNORECASE)
_SNIPPET_LEN = 200


def _fetch_incident(incident_id: str) -> dict[str, Any]:
    container = azure_clients.get_incidents_container()
    try:
        item: Any = container.read_item(item=incident_id, partition_key=incident_id)
    except Exception as exc:
        message = str(exc)
        if "NotFound" in message or "404" in message:
            raise HTTPException(
                status_code=404, detail=f"incident not found: {incident_id}"
            ) from exc
        raise HTTPException(status_code=502, detail=f"cosmos read failed: {message}") from exc
    if not isinstance(item, dict):
        raise HTTPException(status_code=502, detail="cosmos returned non-object incident")
    return item


def _summarize(incident: dict[str, Any]) -> str:
    settings = get_settings()
    client = azure_clients.get_openai_client()
    prompt = (
        "Summarize this incident in 2 sentences and identify the runbook to "
        f"consult: {json.dumps(incident, default=str)}"
    )
    completion: Any = client.chat.completions.create(
        model=settings.azure_openai_chat_deployment,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )
    try:
        content = completion.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise HTTPException(status_code=502, detail="LLM returned malformed payload") from exc
    return str(content or "").strip()


def _recommended_runbook(incident: dict[str, Any], summary: str) -> str | None:
    related = incident.get("relatedRunbook")
    if isinstance(related, str) and related:
        return related
    match = _RUNBOOK_REGEX.search(summary)
    return match.group(0) if match else None


async def handle_summarize_incident(body: dict[str, Any], trace_id: str) -> ToolResponse:
    incident_id = body.get("incident_id")
    if not isinstance(incident_id, str) or not incident_id.strip():
        raise HTTPException(status_code=400, detail="incident_id must be a non-empty string")

    incident = _fetch_incident(incident_id)
    summary = _summarize(incident)
    runbook = _recommended_runbook(incident, summary)

    citations: list[Citation] = [
        Citation(
            type="incident",
            id=incident_id,
            snippet=str(incident.get("summary", ""))[:_SNIPPET_LEN],
        )
    ]
    if runbook:
        citations.append(
            Citation(
                type="runbook",
                id=runbook,
                snippet=f"Runbook recommended for incident {incident_id}.",
            )
        )

    return ToolResponse(
        tool="summarize_incident",
        result={
            "incident": incident,
            "summary": summary,
            "recommended_runbook": runbook,
        },
        citations=citations,
        trace_id=trace_id,
    )

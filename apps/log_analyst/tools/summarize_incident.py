"""summarize_incident tool — Cosmos read + Azure OpenAI summary."""
from __future__ import annotations

import asyncio
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
    """Look up an incident by ``incidentId`` within its own partition.

    We query rather than ``read_item`` because the spec only guarantees
    partition key ``/incidentId``; it does not promise that the Cosmos
    document ``id`` equals the ``incidentId``. A point read would silently
    404 those documents.
    """
    container = azure_clients.get_incidents_container()
    try:
        rows: Any = container.query_items(
            query="SELECT * FROM c WHERE c.incidentId = @id",
            parameters=[{"name": "@id", "value": incident_id}],
            partition_key=incident_id,
        )
        items = list(rows)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"cosmos read failed: {exc}"
        ) from exc
    if not items:
        raise HTTPException(status_code=404, detail=f"incident not found: {incident_id}")
    first = items[0]
    if not isinstance(first, dict):
        raise HTTPException(status_code=502, detail="cosmos returned non-object incident")
    return first


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


def _do_summarize(incident_id: str) -> tuple[dict[str, Any], str, str | None]:
    incident = _fetch_incident(incident_id)
    summary = _summarize(incident)
    runbook = _recommended_runbook(incident, summary)
    return incident, summary, runbook


async def handle_summarize_incident(body: dict[str, Any], trace_id: str) -> ToolResponse:
    incident_id = body.get("incident_id")
    if not isinstance(incident_id, str) or not incident_id.strip():
        raise HTTPException(status_code=400, detail="incident_id must be a non-empty string")

    # Cosmos + OpenAI SDKs are sync — offload to a worker thread.
    incident, summary, runbook = await asyncio.to_thread(_do_summarize, incident_id)

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


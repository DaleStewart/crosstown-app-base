"""Tool registrations.

Importing this module wires every tool into the central registry. The router
discovers tools via :func:`tool_router.list_descriptors`.
"""
from __future__ import annotations

from citations import ToolDescriptor
from tool_router import register
from tools.detect_pattern import handle_detect_pattern
from tools.search_logs import handle_search_logs
from tools.summarize_incident import handle_summarize_incident

register(
    ToolDescriptor(
        name="search_logs",
        description="Hybrid Azure AI Search against the mta-logs index.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "time_range": {
                    "type": ["object", "null"],
                    "properties": {
                        "from": {"type": "string", "format": "date-time"},
                        "to": {"type": "string", "format": "date-time"},
                    },
                    "required": ["from", "to"],
                },
            },
            "required": ["query"],
        },
    ),
    handle_search_logs,
)

register(
    ToolDescriptor(
        name="detect_pattern",
        description=(
            "Given a seed log_id, fetch nearby logs on the same line and match "
            "known multi-event signatures."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "log_id": {"type": "string"},
                "window_minutes": {"type": "integer", "minimum": 1, "default": 60},
            },
            "required": ["log_id"],
        },
    ),
    handle_detect_pattern,
)

register(
    ToolDescriptor(
        name="summarize_incident",
        description="Read an incident from Cosmos and produce an LLM summary.",
        input_schema={
            "type": "object",
            "properties": {"incident_id": {"type": "string"}},
            "required": ["incident_id"],
        },
    ),
    handle_summarize_incident,
)

__all__ = [
    "handle_detect_pattern",
    "handle_search_logs",
    "handle_summarize_incident",
]

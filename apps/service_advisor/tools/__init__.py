"""Tool registrations for the Service Disruption Advisor.

Importing this module wires every tool into the central registry. The router
discovers tools via :func:`tool_router.list_descriptors`.
"""
from __future__ import annotations

from citations import ToolDescriptor
from tool_router import register
from tools.find_alternate_route import handle_find_alternate_route
from tools.get_disruption_status import handle_get_disruption_status
from tools.get_shuttle_bridging import handle_get_shuttle_bridging
from tools.recommend_commute_action import handle_recommend_commute_action

register(
    ToolDescriptor(
        name="get_disruption_status",
        description=(
            "Return the active service disruption (if any) for a rail line. "
            "Use when a rider asks 'is L1 running', 'is there a strike', "
            "'when will service resume', or similar status questions."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "line": {"type": "string", "description": "Line id, e.g. L1, L2, L3"},
            },
            "required": ["line"],
        },
    ),
    handle_get_disruption_status,
)

register(
    ToolDescriptor(
        name="find_alternate_route",
        description=(
            "Suggest a non-disrupted route between two stations, optionally avoiding "
            "a disruption. Use when a rider asks how to get from A to B during an outage."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "disruption_id": {"type": ["string", "null"]},
            },
            "required": ["origin", "destination"],
        },
    ),
    handle_find_alternate_route,
)

register(
    ToolDescriptor(
        name="get_shuttle_bridging",
        description=(
            "Look up the shuttle-bus bridging plan associated with a disruption "
            "and, optionally, filter for whether a specific station is covered."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "disruption_id": {"type": "string"},
                "station": {"type": ["string", "null"]},
            },
            "required": ["disruption_id"],
        },
    ),
    handle_get_shuttle_bridging,
)

register(
    ToolDescriptor(
        name="recommend_commute_action",
        description=(
            "Recommend a commute action (work-from-home, alternate mode, wait) "
            "based on the active disruption affecting a line. Cites RB-13."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "line": {"type": "string"},
                "role_supports_remote": {"type": ["boolean", "null"]},
            },
            "required": ["line"],
        },
    ),
    handle_recommend_commute_action,
)

__all__ = [
    "handle_find_alternate_route",
    "handle_get_disruption_status",
    "handle_get_shuttle_bridging",
    "handle_recommend_commute_action",
]

"""HTTP routing for tools.

The registry maps a tool name to (descriptor, async handler). The handler
receives the parsed JSON body and returns a :class:`ToolResponse`. Routing is
table-driven so adding a tool is a single registration call in
:mod:`tools.__init__`.
"""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from citations import ToolDescriptor, ToolResponse

ToolHandler = Callable[[dict[str, Any], str], Awaitable[ToolResponse]]

_REGISTRY: dict[str, tuple[ToolDescriptor, ToolHandler]] = {}


def register(descriptor: ToolDescriptor, handler: ToolHandler) -> None:
    _REGISTRY[descriptor.name] = (descriptor, handler)


def list_descriptors() -> list[ToolDescriptor]:
    return [desc for desc, _ in _REGISTRY.values()]


def get_handler(name: str) -> ToolHandler | None:
    entry = _REGISTRY.get(name)
    return entry[1] if entry else None


def build_router() -> APIRouter:
    router = APIRouter()

    @router.get("/tools")
    async def list_tools() -> list[ToolDescriptor]:
        return list_descriptors()

    @router.post("/tools/{name}")
    async def dispatch(name: str, request: Request) -> ToolResponse:
        handler = get_handler(name)
        if handler is None:
            raise HTTPException(status_code=404, detail=f"unknown tool: {name}")
        try:
            body: dict[str, Any] = await request.json()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid JSON body") from exc
        trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())
        response = await handler(body, trace_id)
        return response.finalize()

    return router

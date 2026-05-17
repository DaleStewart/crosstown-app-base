"""HTTP routing for tools — mirrors apps/log_analyst/tool_router.py."""
from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

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


def _error_envelope(tool: str, trace_id: str, status: int, detail: str) -> JSONResponse:
    payload = ToolResponse(
        tool=tool,
        result={"error": detail, "status": status},
        citations=[],
        trace_id=trace_id,
        warnings=["error", "uncited"],
    )
    return JSONResponse(status_code=status, content=payload.model_dump())


def build_router() -> APIRouter:
    router = APIRouter()

    @router.get("/tools")
    async def list_tools() -> list[ToolDescriptor]:
        return list_descriptors()

    @router.post("/tools/{name}")
    async def dispatch(name: str, request: Request) -> Any:
        trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())
        handler = get_handler(name)
        if handler is None:
            return _error_envelope(name, trace_id, 404, f"unknown tool: {name}")
        try:
            body_any: Any = await request.json()
        except ValueError:
            return _error_envelope(name, trace_id, 400, "invalid JSON body")
        if not isinstance(body_any, dict):
            return _error_envelope(name, trace_id, 400, "request body must be a JSON object")
        try:
            response = await handler(body_any, trace_id)
        except HTTPException as exc:
            detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
            return _error_envelope(name, trace_id, exc.status_code, detail)
        return response.finalize()

    return router

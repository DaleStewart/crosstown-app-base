from __future__ import annotations

from typing import Any

import httpx
import pytest

from agent.tools import ToolRegistry


def _transport_for(routes: dict[str, Any]) -> httpx.MockTransport:
    def handler(req: httpx.Request) -> httpx.Response:
        key = f"{req.method} {req.url.path}"
        if key not in routes:
            return httpx.Response(404, json={"error": "no route"})
        body = routes[key]
        return httpx.Response(200, json=body)

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_registry_load() -> None:
    transport = _transport_for(
        {
            "GET /tools": {
                "tools": [
                    {
                        "name": "search_logs",
                        "description": "search",
                        "parameters": {"type": "object", "properties": {}},
                    }
                ]
            }
        }
    )
    async with httpx.AsyncClient(transport=transport, base_url="http://x") as client:
        reg = ToolRegistry("http://x")
        specs = await reg.load(client=client)
        assert [s.name for s in specs] == ["search_logs"]
        assert reg.loaded is True


@pytest.mark.asyncio
async def test_registry_load_input_schema() -> None:
    """log-analyst exposes JSON Schema as ``input_schema`` (per ToolDescriptor).

    Regression for Bug #10: the loader must surface that schema to the model so
    required fields like ``log_id`` for detect_pattern aren't hidden.
    """
    schema = {
        "type": "object",
        "properties": {"log_id": {"type": "string"}},
        "required": ["log_id"],
    }
    transport = _transport_for(
        {
            "GET /tools": [
                {
                    "name": "detect_pattern",
                    "description": "match patterns",
                    "input_schema": schema,
                }
            ]
        }
    )
    async with httpx.AsyncClient(transport=transport, base_url="http://x") as client:
        reg = ToolRegistry("http://x")
        specs = await reg.load(client=client)
        assert [s.name for s in specs] == ["detect_pattern"]
        assert specs[0].parameters == schema


@pytest.mark.asyncio
async def test_registry_dispatch() -> None:
    transport = _transport_for(
        {
            "POST /tools/search_logs": {
                "result": "ok",
                "citations": [{"source": "log#1"}],
                "warnings": [],
            }
        }
    )
    async with httpx.AsyncClient(transport=transport, base_url="http://x") as client:
        reg = ToolRegistry("http://x")
        out = await reg.dispatch("search_logs", {"q": "doors"}, client=client)
        assert out["result"] == "ok"
        assert out["citations"][0]["source"] == "log#1"

from __future__ import annotations

from typing import Any

import httpx

from voice.base import ToolSpec


class ToolRegistry:
    def __init__(self, log_analyst_url: str) -> None:
        self._url = log_analyst_url.rstrip("/")
        self._specs: list[ToolSpec] = []
        self._loaded = False

    @property
    def specs(self) -> list[ToolSpec]:
        return list(self._specs)

    @property
    def loaded(self) -> bool:
        return self._loaded

    async def load(self, client: httpx.AsyncClient | None = None) -> list[ToolSpec]:
        owns = client is None
        c = client or httpx.AsyncClient(timeout=10.0)
        try:
            resp = await c.get(f"{self._url}/tools")
            resp.raise_for_status()
            payload = resp.json()
        finally:
            if owns:
                await c.aclose()

        tools_raw = payload.get("tools", payload) if isinstance(payload, dict) else payload
        specs: list[ToolSpec] = []
        if isinstance(tools_raw, list):
            for t in tools_raw:
                if not isinstance(t, dict):
                    continue
                specs.append(
                    ToolSpec(
                        name=str(t.get("name", "")),
                        description=str(t.get("description", "")),
                        parameters=dict(t.get("parameters", {})) or {
                            "type": "object",
                            "properties": {},
                        },
                    )
                )
        self._specs = [s for s in specs if s.name]
        self._loaded = True
        return self.specs

    async def dispatch(
        self,
        name: str,
        arguments: dict[str, Any],
        client: httpx.AsyncClient | None = None,
    ) -> dict[str, Any]:
        owns = client is None
        c = client or httpx.AsyncClient(timeout=30.0)
        try:
            resp = await c.post(f"{self._url}/tools/{name}", json=arguments)
            resp.raise_for_status()
            data = resp.json()
        finally:
            if owns:
                await c.aclose()
        if not isinstance(data, dict):
            return {"result": data}
        return data

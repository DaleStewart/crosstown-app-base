from __future__ import annotations

from typing import Any

import httpx

from voice.base import ToolSpec


class ToolRegistry:
    """Aggregates tool specs from one or more specialist services.

    Accepts either a single base URL (legacy) or a list of URLs. ``load()``
    fans out to each ``GET /tools`` endpoint and builds a name → URL map so
    ``dispatch`` can route each tool call to the service that owns it. Tool
    names must be unique across specialists; later registrations win.
    """

    def __init__(self, urls: str | list[str]) -> None:
        if isinstance(urls, str):
            url_list = [urls]
        else:
            url_list = list(urls)
        self._urls: list[str] = [u.rstrip("/") for u in url_list if u]
        if not self._urls:
            raise ValueError("ToolRegistry requires at least one URL")
        self._tool_to_url: dict[str, str] = {}
        self._specs: list[ToolSpec] = []
        self._loaded = False

    @property
    def specs(self) -> list[ToolSpec]:
        return list(self._specs)

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def urls(self) -> list[str]:
        return list(self._urls)

    async def load(self, client: httpx.AsyncClient | None = None) -> list[ToolSpec]:
        owns = client is None
        c = client or httpx.AsyncClient(timeout=10.0)
        all_specs: list[ToolSpec] = []
        mapping: dict[str, str] = {}
        loaded_any = False
        try:
            for url in self._urls:
                try:
                    resp = await c.get(f"{url}/tools")
                    resp.raise_for_status()
                    payload = resp.json()
                    loaded_any = True
                except Exception:
                    # Best-effort per specialist — a missing service must not
                    # block the others from registering.
                    continue
                tools_raw = (
                    payload.get("tools", payload) if isinstance(payload, dict) else payload
                )
                if not isinstance(tools_raw, list):
                    continue
                for t in tools_raw:
                    if not isinstance(t, dict):
                        continue
                    name = str(t.get("name", ""))
                    if not name:
                        continue
                    schema = t.get("input_schema") or t.get("parameters") or {}
                    all_specs.append(
                        ToolSpec(
                            name=name,
                            description=str(t.get("description", "")),
                            parameters=dict(schema)
                            or {"type": "object", "properties": {}},
                        )
                    )
                    mapping[name] = url
        finally:
            if owns:
                await c.aclose()
        self._specs = all_specs
        self._tool_to_url = mapping
        self._loaded = loaded_any
        return self.specs

    async def dispatch(
        self,
        name: str,
        arguments: dict[str, Any],
        client: httpx.AsyncClient | None = None,
    ) -> dict[str, Any]:
        # Fall back to the first registered URL so callers that ``dispatch``
        # without ``load()`` (legacy tests, single-specialist setups) keep
        # working.
        url = self._tool_to_url.get(name, self._urls[0])
        owns = client is None
        c = client or httpx.AsyncClient(timeout=30.0)
        try:
            resp = await c.post(f"{url}/tools/{name}", json=arguments)
            resp.raise_for_status()
            data = resp.json()
        finally:
            if owns:
                await c.aclose()
        if not isinstance(data, dict):
            return {"result": data}
        return data

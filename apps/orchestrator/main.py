from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

from agent.orchestrator import run_voice_session
from agent.tools import ToolRegistry
from settings import get_settings
from storage.cosmos import ConversationStore, build_store_from_settings
from system_prompt import SYSTEM_PROMPT
from voice.base import Final, ToolCall
from voice.factory import build_provider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    tools = ToolRegistry([settings.log_analyst_url, settings.service_advisor_url])
    try:
        await tools.load()
    except Exception:
        # Best-effort: log analyst may not be up yet.
        pass
    app.state.tools = tools
    app.state.provider = build_provider(settings)
    app.state.store = build_store_from_settings()
    app.state.settings = settings
    yield


app = FastAPI(title="MTA Orchestrator", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, Any]:
    settings = get_settings()
    provider_name = getattr(app.state, "provider", None)
    return {
        "status": "ok",
        "service": "orchestrator",
        "voice_provider": settings.voice_provider,
        "provider_name": getattr(provider_name, "name", None),
        "tools_loaded": getattr(app.state, "tools", None) is not None
        and getattr(app.state.tools, "loaded", False),
    }


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict[str, Any]:
    store: ConversationStore | None = getattr(app.state, "store", None)
    if store is None or not store.enabled:
        raise HTTPException(status_code=404, detail="store not configured")
    doc = await store.get(conversation_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="not found")
    return doc


class TurnRequest(BaseModel):
    text: str


class TurnToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]
    call_id: str = ""


class TurnResponse(BaseModel):
    text: str
    citations: list[dict[str, Any]]
    tool_calls: list[TurnToolCall] = []
    warnings: list[str] = []


@app.post("/api/turn", response_model=TurnResponse)
async def api_turn(body: TurnRequest) -> TurnResponse:
    """Text-only single-turn endpoint.

    Used by the evals/redteam harnesses and by clients that don't want voice.
    Reuses the same provider + tool routing path as the WebSocket flow so the
    safety/citation contract is identical.
    """
    provider = getattr(app.state, "provider", None)
    tools = getattr(app.state, "tools", None)
    if provider is None or tools is None or not isinstance(tools, ToolRegistry):
        raise HTTPException(status_code=503, detail="orchestrator not initialized")

    session = await provider.open_session(SYSTEM_PROMPT, tools.specs)
    citations: list[dict[str, Any]] = []
    warnings: list[str] = []
    tool_calls: list[TurnToolCall] = []
    final_text = ""
    try:
        await session.send_text(body.text)
        async for ev in session.events():
            if isinstance(ev, ToolCall):
                tool_calls.append(
                    TurnToolCall(name=ev.name, arguments=dict(ev.arguments), call_id=ev.call_id)
                )
                try:
                    result = await tools.dispatch(ev.name, ev.arguments)
                except Exception as exc:  # pragma: no cover - defensive
                    result = {"error": str(exc), "citations": [], "warnings": [str(exc)]}
                cs = result.get("citations") if isinstance(result, dict) else None
                if isinstance(cs, list):
                    citations.extend(c for c in cs if isinstance(c, dict))
                ws = result.get("warnings") if isinstance(result, dict) else None
                if isinstance(ws, list):
                    warnings.extend(str(w) for w in ws)
                await session.submit_tool_result(ev.call_id, result)
            elif isinstance(ev, Final):
                final_text = ev.text
                if isinstance(ev.citations, list):
                    citations.extend(c for c in ev.citations if isinstance(c, dict))
                break
    finally:
        await session.close()

    if not citations and "uncited" not in warnings:
        warnings.append("uncited")

    return TurnResponse(
        text=final_text,
        citations=citations,
        tool_calls=tool_calls,
        warnings=warnings,
    )


@app.websocket("/ws/voice")
async def ws_voice(ws: WebSocket) -> None:
    provider = app.state.provider
    tools = app.state.tools
    store = app.state.store
    await run_voice_session(ws, provider, tools, store)

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket

from agent.orchestrator import run_voice_session
from agent.tools import ToolRegistry
from settings import get_settings
from storage.cosmos import ConversationStore, build_store_from_settings
from voice.factory import build_provider


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    tools = ToolRegistry(settings.log_analyst_url)
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


@app.websocket("/ws/voice")
async def ws_voice(ws: WebSocket) -> None:
    provider = app.state.provider
    tools = app.state.tools
    store = app.state.store
    await run_voice_session(ws, provider, tools, store)

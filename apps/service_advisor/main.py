"""Service Disruption Advisor FastAPI entrypoint.

Rider-facing specialist that answers questions during a major service
disruption (e.g., a full-line suspension). Mirrors the shape of the
log_analyst service: a ``/tools`` discovery endpoint plus ``/tools/{name}``
dispatch, all responses wrapped in the cited :class:`ToolResponse` envelope.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

import tools  # noqa: F401  — side-effect: register tools
from settings import get_settings
from tool_router import build_router


def _configure_otel() -> None:
    settings = get_settings()
    if settings.app_mode == "test":
        return
    conn = settings.applicationinsights_connection_string
    if not conn:
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=conn,
            service_name=settings.otel_service_name,
        )
    except Exception:
        # Best-effort: never block startup on telemetry.
        pass


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _configure_otel()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="MTA Service Disruption Advisor", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok"}

    app.include_router(build_router())
    return app


app = create_app()

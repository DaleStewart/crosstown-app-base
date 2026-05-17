"""FastAPI entrypoint for the Log Analyst service."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

import tools  # noqa: F401  — registers tools on import
from settings import get_settings
from tool_router import build_router

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

log = logging.getLogger("log_analyst")


def _configure_otel() -> None:
    settings = get_settings()
    if not settings.applicationinsights_connection_string:
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=settings.applicationinsights_connection_string,
            service_name=settings.otel_service_name,
        )
    except Exception:  # pragma: no cover - observability must not crash startup
        log.exception("Failed to configure Azure Monitor OpenTelemetry")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _configure_otel()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="MTA Log Analyst",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "log_analyst"}

    app.include_router(build_router())
    return app


app = create_app()

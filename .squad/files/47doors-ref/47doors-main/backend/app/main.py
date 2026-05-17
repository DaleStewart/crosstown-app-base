"""
FastAPI application entry point for the Front Door Support Agent.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.api.media_ws import router as media_ws_router
from app.api.phone import router as phone_router
from app.api.realtime import router as realtime_router
from app.api.transcripts import router as transcripts_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Mock mode: {settings.use_mock_services}")

    yield

    # Shutdown
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        Universal Front Door Support Agent API

        A three-agent system that routes student support requests to appropriate
        departments, creates tickets, and retrieves relevant knowledge base articles.

        ## Features

        - **Intent Detection**: Analyze natural language queries to detect intent
        - **Smart Routing**: Route requests to the correct department
        - **Ticket Creation**: Create support tickets automatically
        - **Knowledge Base**: Retrieve relevant help articles
        - **Human Escalation**: Escalate complex issues to human reviewers

        ## Authentication

        Most endpoints require a Bearer JWT token from university SSO.
        The `/api/knowledge/search` and `/api/health` endpoints are public.
        """,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        lifespan=lifespan,
    )

    # Configure CORS - allow all origins in development
    if settings.environment == "development":
        origins = ["*"]
    else:
        origins = settings.allowed_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router, prefix=settings.api_prefix)
    app.include_router(realtime_router, prefix=f"{settings.api_prefix}/realtime", tags=["Voice Realtime"])
    app.include_router(phone_router, prefix=f"{settings.api_prefix}/phone", tags=["Phone Call Automation"])
    app.include_router(transcripts_router, prefix=f"{settings.api_prefix}/phone", tags=["Phone Transcripts"])
    app.include_router(media_ws_router, prefix="/ws", tags=["Media WebSocket"])

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

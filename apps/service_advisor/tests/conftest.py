"""Test fixtures for the Service Disruption Advisor.

Forces ``APP_MODE=test`` before any project module is imported and provides an
ASGI httpx client wired to the FastAPI app.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

os.environ.setdefault("APP_MODE", "test")

import httpx
import pytest_asyncio

import data_loader
from main import app


@pytest_asyncio.fixture(autouse=True)
async def _reset_data_cache() -> AsyncIterator[None]:
    data_loader.reset_cache()
    yield
    data_loader.reset_cache()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

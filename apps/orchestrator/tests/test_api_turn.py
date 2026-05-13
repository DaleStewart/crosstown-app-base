from __future__ import annotations

from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import main
from agent.tools import ToolRegistry
from main import app
from tests.conftest import FakeProvider, FakeSession, Final, ToolCall


class _StubRegistry(ToolRegistry):
    def __init__(self, response: dict[str, Any]) -> None:
        super().__init__("http://fake")
        self._response = response

    async def dispatch(
        self,
        name: str,
        arguments: dict[str, Any],
        client: httpx.AsyncClient | None = None,
    ) -> dict[str, Any]:
        del name, arguments, client
        return self._response


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_api_turn_returns_text_and_citations(client: TestClient) -> None:
    session = FakeSession()
    session.queue(ToolCall(name="search_logs", arguments={"query": "x"}, call_id="c1"))
    session.queue(Final(text="Doors held cluster at Beacon on L2.", citations=[]))
    app.state.provider = FakeProvider(session)
    app.state.tools = _StubRegistry(
        {
            "result": {"hits": []},
            "citations": [
                {"type": "log", "id": "L-000123", "snippet": "doors.held sample"}
            ],
            "warnings": [],
        }
    )

    resp = client.post("/api/turn", json={"text": "anything wrong on L2?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["text"] == "Doors held cluster at Beacon on L2."
    assert any(c["id"] == "L-000123" for c in body["citations"])
    assert "uncited" not in body["warnings"]


def test_api_turn_marks_uncited_when_no_citations(client: TestClient) -> None:
    session = FakeSession()
    session.queue(Final(text="I have nothing.", citations=[]))
    app.state.provider = FakeProvider(session)
    app.state.tools = _StubRegistry({"result": {}, "citations": [], "warnings": []})

    resp = client.post("/api/turn", json={"text": "tell me about L9"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["citations"] == []
    assert "uncited" in body["warnings"]


def test_api_turn_returns_503_when_not_initialized(client: TestClient) -> None:
    # Force missing provider on a fresh app instance to avoid leaking state.
    fresh = FastAPI()
    for route in app.routes:
        fresh.routes.append(route)
    # Strip provider/tools off the new app.state.
    fresh.state.provider = None
    fresh.state.tools = None
    c = TestClient(fresh)
    # We patch the global app.state for /api/turn since the route reads app.state directly.
    saved_provider = getattr(app.state, "provider", None)
    saved_tools = getattr(app.state, "tools", None)
    app.state.provider = None
    app.state.tools = None
    try:
        resp = c.post("/api/turn", json={"text": "x"})
        assert resp.status_code == 503
    finally:
        app.state.provider = saved_provider
        app.state.tools = saved_tools


# Silence unused-import warnings
_ = main

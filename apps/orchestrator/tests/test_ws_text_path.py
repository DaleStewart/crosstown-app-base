from __future__ import annotations

import json
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

import main as main_module
from agent.tools import ToolRegistry
from storage.cosmos import ConversationStore
from tests.conftest import FakeContainer, FakeProvider, FakeSession
from voice.base import Final, ToolCall, TranscriptDelta


@pytest.fixture
def client_with_fakes(monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, FakeSession]:
    fake_session = FakeSession()
    fake_session.queue(TranscriptDelta(role="user", text="hello", final=True))
    fake_session.queue(
        ToolCall(name="search_logs", arguments={"q": "doors"}, call_id="c1")
    )
    fake_session.queue(Final(text="done", citations=[{"source": "log#1"}]))
    provider = FakeProvider(fake_session)

    container = FakeContainer()
    store = ConversationStore(container)

    reg = ToolRegistry("http://x")
    reg._specs = []  # noqa: SLF001
    reg._loaded = True  # noqa: SLF001

    async def fake_dispatch(
        name: str, args: dict[str, Any], client: httpx.AsyncClient | None = None
    ) -> dict[str, Any]:
        return {"result": "ok", "citations": [{"source": "log#1"}], "warnings": []}

    monkeypatch.setattr(reg, "dispatch", fake_dispatch)

    # Replace lifespan-built state with our fakes by overriding the lifespan.
    main_module.app.state.provider = provider
    main_module.app.state.tools = reg
    main_module.app.state.store = store

    client = TestClient(main_module.app)
    return client, fake_session


def test_health(client_with_fakes: tuple[TestClient, FakeSession]) -> None:
    client, _ = client_with_fakes
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "orchestrator"


def test_ws_text_round_trip(
    client_with_fakes: tuple[TestClient, FakeSession],
) -> None:
    client, fake_session = client_with_fakes
    with client.websocket_connect("/ws/voice") as ws:
        ws.send_text(
            json.dumps(
                {"type": "start", "conversationId": "abc-123", "mode": "push_to_talk"}
            )
        )
        ws.send_text(json.dumps({"type": "text", "text": "any doors-held errors?"}))

        seen_types: list[str] = []
        for _ in range(10):
            try:
                frame = ws.receive_text()
            except Exception:
                break
            seen_types.append(json.loads(frame)["type"])
            if "final" in seen_types:
                break
        ws.send_text(json.dumps({"type": "stop"}))

    assert "transcript_delta" in seen_types
    assert "tool_call" in seen_types
    assert "tool_result" in seen_types
    assert "final" in seen_types
    assert fake_session.closed is True
    assert fake_session.tool_results and fake_session.tool_results[0][0] == "c1"

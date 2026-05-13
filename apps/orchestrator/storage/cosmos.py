from __future__ import annotations

import datetime as _dt
from typing import Any, Protocol


class _AsyncContainerProto(Protocol):
    async def upsert_item(self, body: dict[str, Any]) -> dict[str, Any]: ...

    async def read_item(self, item: str, partition_key: str) -> dict[str, Any]: ...


class ConversationStore:
    """Cosmos-backed persistence for conversation turns.

    The container is injected so tests can pass a fake.
    """

    def __init__(self, container: _AsyncContainerProto | None) -> None:
        self._container = container

    @property
    def enabled(self) -> bool:
        return self._container is not None

    async def upsert_turn(self, conversation_id: str, turn: dict[str, Any]) -> None:
        if self._container is None:
            return
        now = _dt.datetime.now(_dt.UTC).isoformat()
        existing: dict[str, Any]
        try:
            existing = await self._container.read_item(
                item=conversation_id, partition_key=conversation_id
            )
        except Exception:
            existing = {
                "id": conversation_id,
                "conversationId": conversation_id,
                "turns": [],
                "createdAt": now,
            }
        turns = list(existing.get("turns", []))
        turns.append({**turn, "ts": now})
        existing["turns"] = turns
        existing["updatedAt"] = now
        existing.setdefault("createdAt", now)
        await self._container.upsert_item(existing)

    async def get(self, conversation_id: str) -> dict[str, Any] | None:
        if self._container is None:
            return None
        try:
            return await self._container.read_item(
                item=conversation_id, partition_key=conversation_id
            )
        except Exception:
            return None


def build_store_from_settings() -> ConversationStore:
    """Construct a real Cosmos-backed store; returns a no-op store on failure."""
    from settings import get_settings

    s = get_settings()
    if not s.azure_cosmos_endpoint:
        return ConversationStore(None)
    try:
        from azure.cosmos.aio import CosmosClient
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential()
        client = CosmosClient(s.azure_cosmos_endpoint, credential=credential)
        db = client.get_database_client(s.azure_cosmos_database)
        container = db.get_container_client(s.azure_cosmos_container_conversations)
        return ConversationStore(container)  # type: ignore[arg-type]
    except Exception:
        return ConversationStore(None)

"""Test fixtures.

Forces APP_MODE=test before any project module imports so settings does not
demand real Azure config, then monkey-patches azure_clients getters with
in-memory fakes so tools execute without network calls.
"""
from __future__ import annotations

import os
import re
from collections.abc import AsyncIterator, Iterator
from typing import Any

os.environ.setdefault("APP_MODE", "test")

import httpx
import pytest
import pytest_asyncio

import azure_clients
from main import app


def _filter_match(odata: str, doc: dict[str, Any]) -> bool:
    """Minimal OData parser for our two query shapes."""
    eq_pairs = re.findall(r"(\w+)\s+eq\s+'([^']*)'", odata)
    for field, value in eq_pairs:
        if str(doc.get(field, "")) != value:
            return False
    ge_pairs = re.findall(r"(\w+)\s+ge\s+([^\s)]+)", odata)
    for field, value in ge_pairs:
        if str(doc.get(field, "")) < value:
            return False
    le_pairs = re.findall(r"(\w+)\s+le\s+([^\s)]+)", odata)
    return all(str(doc.get(field, "")) <= value for field, value in le_pairs)


class FakeSearchClient:
    """In-memory stand-in for azure.search.documents.SearchClient."""

    def __init__(self, docs: list[dict[str, Any]] | None = None) -> None:
        self.docs: list[dict[str, Any]] = list(docs or [])
        self.calls: list[dict[str, Any]] = []

    def add(self, *docs: dict[str, Any]) -> None:
        self.docs.extend(docs)

    def search(
        self,
        *,
        search_text: str,
        filter: str | None = None,
        top: int = 10,
        **_: Any,
    ) -> list[dict[str, Any]]:
        self.calls.append({"search_text": search_text, "filter": filter, "top": top})
        results = list(self.docs)
        if filter:
            results = [d for d in results if _filter_match(filter, d)]
        if search_text and search_text != "*":
            needle = search_text.lower()
            results = [d for d in results if needle in str(d.get("message", "")).lower()]
        return results[:top]


class FakeIncidentsContainer:
    def __init__(self, items: dict[str, dict[str, Any]] | None = None) -> None:
        self.items: dict[str, dict[str, Any]] = dict(items or {})

    def read_item(self, *, item: str, partition_key: str) -> dict[str, Any]:
        if item not in self.items:
            raise RuntimeError(f"NotFound: {item}")
        assert partition_key == item
        return self.items[item]


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeChatCompletions:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> _FakeCompletion:
        self.calls.append(kwargs)
        return _FakeCompletion(self.response_text)


class _FakeChat:
    def __init__(self, response_text: str) -> None:
        self.completions = _FakeChatCompletions(response_text)


class FakeOpenAIClient:
    def __init__(
        self,
        response_text: str = "Two-sentence summary. Consult RB-05-interlock-fault.",
    ) -> None:
        self.chat = _FakeChat(response_text)


@pytest.fixture
def fake_search() -> FakeSearchClient:
    return FakeSearchClient()


@pytest.fixture
def fake_cosmos() -> FakeIncidentsContainer:
    return FakeIncidentsContainer()


@pytest.fixture
def fake_openai() -> FakeOpenAIClient:
    return FakeOpenAIClient()


@pytest.fixture(autouse=True)
def _patch_clients(
    monkeypatch: pytest.MonkeyPatch,
    fake_search: FakeSearchClient,
    fake_cosmos: FakeIncidentsContainer,
    fake_openai: FakeOpenAIClient,
) -> Iterator[None]:
    monkeypatch.setattr(azure_clients, "get_search_client", lambda: fake_search)
    monkeypatch.setattr(azure_clients, "get_incidents_container", lambda: fake_cosmos)
    monkeypatch.setattr(azure_clients, "get_openai_client", lambda: fake_openai)
    yield


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

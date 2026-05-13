"""Cached singleton Azure SDK clients.

Tests monkey-patch the module-level getters in :mod:`conftest` with fakes, so
keep the public surface intentionally minimal.
"""
from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from azure.identity import DefaultAzureCredential

from settings import get_settings

if TYPE_CHECKING:  # pragma: no cover - import guards for typing only
    from azure.cosmos import ContainerProxy
    from azure.search.documents import SearchClient
    from openai import AzureOpenAI


@lru_cache(maxsize=1)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


@lru_cache(maxsize=1)
def get_search_client() -> SearchClient:
    from azure.search.documents import SearchClient  # local import to keep cold-start cheap

    settings = get_settings()
    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT is not configured")
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index_logs,
        credential=_credential(),
    )


@lru_cache(maxsize=1)
def get_incidents_container() -> ContainerProxy:
    from azure.cosmos import CosmosClient

    settings = get_settings()
    if not settings.azure_cosmos_endpoint:
        raise RuntimeError("AZURE_COSMOS_ENDPOINT is not configured")
    client = CosmosClient(settings.azure_cosmos_endpoint, credential=_credential())
    db = client.get_database_client(settings.azure_cosmos_database)
    container: Any = db.get_container_client(settings.azure_cosmos_container_incidents)
    return container  # type: ignore[no-any-return]  # azure-cosmos stubs are loose


@lru_cache(maxsize=1)
def get_openai_client() -> AzureOpenAI:
    from azure.identity import get_bearer_token_provider
    from openai import AzureOpenAI

    settings = get_settings()
    if not settings.azure_openai_endpoint:
        raise RuntimeError("AZURE_OPENAI_ENDPOINT is not configured")
    token_provider = get_bearer_token_provider(
        _credential(), "https://cognitiveservices.azure.com/.default"
    )
    return AzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        azure_ad_token_provider=token_provider,
    )


def reset_cache() -> None:
    """Clear cached singletons. Used by tests."""
    _credential.cache_clear()
    get_search_client.cache_clear()
    get_incidents_container.cache_clear()
    get_openai_client.cache_clear()

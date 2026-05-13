"""Runtime configuration.

All Azure-backed fields are optional so that the unit tests can import this
module without environment variables set. A model validator fails loud at
process start when ``APP_MODE`` is not ``test`` and a required Azure value is
missing.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_mode: Literal["prod", "test"] = Field(
        default="prod",
        description="When 'test', missing Azure config is tolerated.",
    )

    # Azure OpenAI
    azure_openai_endpoint: str | None = None
    azure_openai_chat_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-08-01-preview"

    # Azure AI Search
    azure_search_endpoint: str | None = None
    azure_search_index_logs: str = "mta-logs"
    azure_search_index_runbooks: str = "mta-runbooks"

    # Cosmos DB
    azure_cosmos_endpoint: str | None = None
    azure_cosmos_database: str = "mta"
    azure_cosmos_container_incidents: str = "incidents"

    # Observability
    applicationinsights_connection_string: str | None = None
    otel_service_name: str = "mta-log-analyst"

    @model_validator(mode="after")
    def _require_in_prod(self) -> Settings:
        if self.app_mode == "test":
            return self
        missing: list[str] = []
        if not self.azure_search_endpoint:
            missing.append("AZURE_SEARCH_ENDPOINT")
        if not self.azure_cosmos_endpoint:
            missing.append("AZURE_COSMOS_ENDPOINT")
        if not self.azure_openai_endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(missing)
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Default to test mode if pytest is running so imports stay cheap.
    if "PYTEST_CURRENT_TEST" in os.environ and "APP_MODE" not in os.environ:
        os.environ["APP_MODE"] = "test"
    return Settings()

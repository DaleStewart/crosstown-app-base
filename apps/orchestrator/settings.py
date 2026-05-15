from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    voice_provider: str = "foundry_realtime"

    azure_ai_foundry_project_endpoint: str = ""
    azure_openai_chat_deployment: str = "gpt-4.1"
    azure_openai_realtime_deployment: str = "gpt-realtime-1.5"

    azure_speech_endpoint: str = ""
    azure_speech_region: str = "eastus2"

    azure_cosmos_endpoint: str = ""
    azure_cosmos_database: str = "mta"
    azure_cosmos_container_conversations: str = "conversations"

    log_analyst_url: str = "http://localhost:8001"

    otel_service_name: str = "mta-orchestrator"
    applicationinsights_connection_string: str = ""

    use_local_auth: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

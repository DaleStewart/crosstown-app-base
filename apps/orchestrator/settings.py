from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    voice_provider: str = "foundry_realtime"

    azure_ai_foundry_project_endpoint: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_chat_deployment: str = "gpt-4.1"
    azure_openai_realtime_deployment: str = "gpt-realtime-1.5"
    # Deployment name for input audio transcription (user speech → text).
    # Azure OpenAI requires an *existing* deployment name — "whisper-1" is NOT valid
    # because no whisper deployment is provisioned in infra/modules/foundry.bicep.
    # OpenAI (non-Azure) accepts "whisper-1". Set to "" to disable transcription;
    # the voice loop continues without user transcript rather than crashing.
    # Add a whisper-1 or gpt-4o-transcribe deployment to foundry.bicep, then set
    # AZURE_OPENAI_TRANSCRIPTION_DEPLOYMENT=<name> to enable.
    azure_openai_transcription_deployment: str = ""

    azure_speech_endpoint: str = ""
    azure_speech_region: str = "eastus2"

    azure_cosmos_endpoint: str = ""
    azure_cosmos_database: str = "mta"
    azure_cosmos_container_conversations: str = "conversations"

    log_analyst_url: str = "http://localhost:8001"
    service_advisor_url: str = "http://localhost:8002"

    otel_service_name: str = "mta-orchestrator"
    applicationinsights_connection_string: str = ""

    use_local_auth: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

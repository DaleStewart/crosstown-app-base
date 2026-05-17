"""
Application configuration using Pydantic Settings.
Supports both environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application Settings
    # ==========================================================================
    app_name: str = Field(default="Front Door Support Agent")
    app_version: str = Field(default="1.0.0")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development"
    )
    debug: bool = Field(default=False)
    mock_mode: bool = Field(
        default=True,
        description="Use mock implementations for external services"
    )

    # ==========================================================================
    # API Settings
    # ==========================================================================
    api_prefix: str = Field(default="/api")
    allowed_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    # ==========================================================================
    # Azure OpenAI Settings
    # ==========================================================================
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        default="",
        description="Azure OpenAI API key (optional - uses managed identity if not provided)"
    )
    azure_openai_deployment: str = Field(
        default="gpt-4.1",
        description="Azure OpenAI deployment name"
    )
    azure_openai_api_version: str = Field(
        default="2025-04-01-preview",
        description="Azure OpenAI API version"
    )

    # ==========================================================================
    # Azure Cosmos DB Settings
    # ==========================================================================
    cosmos_db_endpoint: str = Field(
        default="",
        description="Azure Cosmos DB endpoint URL"
    )
    cosmos_db_key: str = Field(
        default="",
        description="Azure Cosmos DB primary key"
    )
    cosmos_db_database: str = Field(
        default="frontdoor",
        description="Cosmos DB database name"
    )
    cosmos_db_sessions_container: str = Field(
        default="sessions",
        description="Container for session data"
    )
    cosmos_db_audit_container: str = Field(
        default="audit_logs",
        description="Container for audit logs"
    )

    # ==========================================================================
    # Azure AI Search Settings
    # ==========================================================================
    azure_search_endpoint: str = Field(
        default="",
        description="Azure AI Search endpoint URL"
    )
    azure_search_key: str = Field(
        default="",
        description="Azure AI Search API key"
    )
    azure_search_index: str = Field(
        default="knowledge-base",
        description="Search index name"
    )

    # ==========================================================================
    # ServiceNow Settings
    # ==========================================================================
    servicenow_instance: str = Field(
        default="",
        description="ServiceNow instance URL (e.g., 'university.service-now.com')"
    )
    servicenow_api_key: str = Field(
        default="",
        description="ServiceNow API key"
    )
    servicenow_username: str = Field(
        default="",
        description="ServiceNow username (for basic auth if needed)"
    )
    servicenow_password: str = Field(
        default="",
        description="ServiceNow password (for basic auth if needed)"
    )

    # ==========================================================================
    # Session Settings
    # ==========================================================================
    session_ttl_seconds: int = Field(
        default=7776000,  # 90 days
        description="Session time-to-live in seconds"
    )
    max_clarification_attempts: int = Field(
        default=3,
        description="Maximum clarification attempts before escalation"
    )
    max_conversation_turns: int = Field(
        default=50,
        description="Maximum conversation turns to keep in history"
    )

    # ==========================================================================
    # Confidence Thresholds
    # ==========================================================================
    confidence_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for routing without clarification"
    )
    kb_relevance_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score for KB articles"
    )

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per window"
    )
    rate_limit_window_seconds: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )

    # ==========================================================================
    # SLA Configuration (hours)
    # ==========================================================================
    sla_urgent_hours: int = Field(default=1)
    sla_high_hours: int = Field(default=4)
    sla_medium_hours: int = Field(default=24)
    sla_low_hours: int = Field(default=72)

    # ==========================================================================
    # Voice / Realtime API Settings
    # ==========================================================================
    voice_enabled: bool = Field(
        default=True,
        description="Kill switch for the voice feature; auto-disabled when deployment is unset outside mock mode"
    )
    azure_openai_realtime_deployment: str = Field(
        default="",
        description="Azure OpenAI Realtime API deployment name (e.g. gpt-realtime)"
    )
    azure_openai_realtime_api_version: str = Field(
        default="2025-04-01-preview",
        description="API version for the Azure OpenAI Realtime endpoint"
    )
    realtime_voice: str = Field(
        default="marin",
        description="Azure OpenAI voice selection for Realtime API (e.g. marin, cedar, alloy, shimmer, echo)"
    )
    realtime_vad_threshold_ms: int = Field(
        default=500,
        description="Voice Activity Detection silence threshold in milliseconds"
    )
    max_voice_session_duration: int = Field(
        default=600,
        description="Maximum voice session duration in seconds (default 10 minutes)"
    )

    # ==========================================================================
    # Phone / Azure Communication Services Settings
    # ==========================================================================
    phone_enabled: bool = Field(
        default=True,
        description="Kill switch for phone call feature; auto-disabled when ACS endpoint is unset outside mock mode"
    )
    azure_acs_endpoint: str = Field(
        default="",
        description="Azure Communication Services endpoint URL"
    )
    azure_acs_connection_string: str = Field(
        default="",
        description="ACS connection string for Call Automation (optional - uses managed identity if not provided)"
    )
    acs_phone_number: str = Field(
        default="",
        description="Phone number provisioned in ACS for inbound calls (E.164 format, e.g. +15551234567)"
    )
    phone_callback_base_url: str = Field(
        default="",
        description="Public HTTPS base URL for ACS call-back webhooks. "
                    "When empty, inferred from X-Forwarded-Proto/Host headers."
    )
    max_call_duration: int = Field(
        default=600,
        description="Maximum phone call duration in seconds (default 10 minutes)"
    )

    @model_validator(mode="after")
    def _auto_disable_features(self) -> "Settings":
        """Auto-disable voice and phone when not configured outside mock mode."""
        if not self.azure_openai_realtime_deployment and not self.mock_mode:
            self.voice_enabled = False
        if not self.azure_acs_endpoint and not self.mock_mode:
            self.phone_enabled = False
        return self

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "test"

    @property
    def use_mock_services(self) -> bool:
        """Determine if mock services should be used."""
        return self.mock_mode or self.is_test


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

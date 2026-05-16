"""Runtime configuration for the Service Disruption Advisor.

Data ships bundled with the service (see ``data_loader``), so the only optional
Azure dependency is OpenTelemetry export to App Insights.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_mode: Literal["prod", "test"] = Field(
        default="prod",
        description="When 'test', skips OTel wiring.",
    )

    applicationinsights_connection_string: str | None = None
    otel_service_name: str = "mta-service-advisor"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    if "PYTEST_CURRENT_TEST" in os.environ and "APP_MODE" not in os.environ:
        os.environ["APP_MODE"] = "test"
    return Settings()

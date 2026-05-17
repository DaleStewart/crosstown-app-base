"""Tests for voice configuration fields in Settings."""
import pytest
from app.core.config import Settings


class TestVoiceConfig:
    """Voice configuration validation tests."""

    def test_voice_enabled_defaults_true_in_mock_mode(self):
        """voice_enabled should default True when mock_mode=True."""
        settings = Settings(mock_mode=True)
        assert settings.voice_enabled is True

    def test_voice_enabled_auto_false_when_no_deployment_production(self):
        """voice_enabled auto-set False when deployment empty and mock_mode=False."""
        settings = Settings(
            mock_mode=False,
            azure_openai_realtime_deployment="",
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            azure_openai_deployment="gpt-4.1",
        )
        assert settings.voice_enabled is False

    def test_voice_enabled_true_when_deployment_set(self):
        """voice_enabled stays True when deployment is configured."""
        settings = Settings(
            mock_mode=False,
            azure_openai_realtime_deployment="gpt-realtime",
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_api_key="test-key",
            azure_openai_deployment="gpt-4.1",
        )
        assert settings.voice_enabled is True

    def test_vad_threshold_accepts_valid_integer(self):
        """realtime_vad_threshold_ms should accept valid integer values."""
        settings = Settings(mock_mode=True, realtime_vad_threshold_ms=300)
        assert settings.realtime_vad_threshold_ms == 300

    def test_vad_threshold_default_is_500(self):
        """realtime_vad_threshold_ms should default to 500 ms."""
        settings = Settings(mock_mode=True)
        assert settings.realtime_vad_threshold_ms == 500

    def test_max_voice_session_duration_default(self):
        """max_voice_session_duration defaults to 600 seconds."""
        settings = Settings(mock_mode=True)
        assert settings.max_voice_session_duration == 600

    def test_max_voice_session_duration_custom(self):
        """max_voice_session_duration accepts custom values."""
        settings = Settings(mock_mode=True, max_voice_session_duration=300)
        assert settings.max_voice_session_duration == 300

    def test_realtime_api_version_default(self):
        """API version should have a sensible default."""
        settings = Settings(mock_mode=True)
        assert settings.azure_openai_realtime_api_version == "2025-04-01-preview"

    def test_realtime_voice_default_marin(self):
        """Default voice should be marin."""
        settings = Settings(mock_mode=True)
        assert settings.realtime_voice == "marin"

    def test_realtime_deployment_field_accepts_empty_string(self):
        """Realtime deployment field should accept an empty string value."""
        settings = Settings(mock_mode=True, azure_openai_realtime_deployment="")
        assert settings.azure_openai_realtime_deployment == ""

    def test_voice_enabled_remains_true_in_mock_mode_even_without_deployment(self):
        """In mock mode, voice stays enabled even with no realtime deployment."""
        settings = Settings(mock_mode=True, azure_openai_realtime_deployment="")
        assert settings.voice_enabled is True

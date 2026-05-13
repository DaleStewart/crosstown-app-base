from __future__ import annotations

from settings import Settings, get_settings
from voice.foundry_realtime import FoundryRealtimeProvider
from voice.speech_services import SpeechServicesProvider

Provider = FoundryRealtimeProvider | SpeechServicesProvider


def build_provider(settings: Settings | None = None) -> Provider:
    s = settings or get_settings()
    choice = (s.voice_provider or "foundry_realtime").strip().lower()
    if choice == "speech_services":
        return SpeechServicesProvider(
            speech_endpoint=s.azure_speech_endpoint,
            speech_region=s.azure_speech_region,
            chat_deployment=s.azure_openai_chat_deployment,
        )
    return FoundryRealtimeProvider(
        endpoint=s.azure_ai_foundry_project_endpoint,
        deployment=s.azure_openai_realtime_deployment,
    )

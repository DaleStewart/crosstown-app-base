from __future__ import annotations

from settings import Settings
from voice.factory import build_provider
from voice.foundry_realtime import FoundryRealtimeProvider
from voice.speech_services import SpeechServicesProvider


def test_default_is_foundry() -> None:
    s = Settings(voice_provider="")
    p = build_provider(s)
    assert isinstance(p, FoundryRealtimeProvider)
    assert p.name == "foundry_realtime"


def test_foundry_explicit() -> None:
    s = Settings(voice_provider="foundry_realtime")
    p = build_provider(s)
    assert isinstance(p, FoundryRealtimeProvider)


def test_speech_services() -> None:
    s = Settings(voice_provider="speech_services")
    p = build_provider(s)
    assert isinstance(p, SpeechServicesProvider)
    assert p.name == "speech_services"


def test_case_insensitive() -> None:
    s = Settings(voice_provider="Speech_Services")
    p = build_provider(s)
    assert isinstance(p, SpeechServicesProvider)

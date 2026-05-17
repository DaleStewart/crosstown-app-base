"""Voice-specific enumerations for the 47 Doors voice interaction feature."""

from enum import Enum


class VoiceSessionStatus(str, Enum):
    """Server-side lifecycle status of a voice session."""
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"


class VoiceRole(str, Enum):
    """Speaker role in a voice transcript entry."""
    USER = "user"
    ASSISTANT = "assistant"

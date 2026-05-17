"""
Mock phone service for testing and demo mode.
Returns deterministic responses without requiring Azure Communication Services credentials.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.services.azure.phone import PHONE_SYSTEM_PROMPT  # single source of truth
from app.services.interfaces import PhoneServiceInterface

logger = logging.getLogger(__name__)


class MockPhoneService(PhoneServiceInterface):
    """Mock implementation of the ACS Call Automation phone service."""

    def handle_incoming_call(
        self,
        incoming_call_context: str,
        caller_id: str,
        callback_url: str,
    ) -> dict:
        """Return a deterministic mock call connection response."""
        call_connection_id = f"mock-call-{uuid4().hex[:12]}"
        logger.info(
            f"MockPhoneService: answered call from {caller_id}, "
            f"connection_id={call_connection_id}"
        )
        self._last_call = {
            "call_connection_id": call_connection_id,
            "caller_id": caller_id,
            "incoming_call_context": incoming_call_context,
            "callback_url": callback_url,
            "system_prompt": PHONE_SYSTEM_PROMPT,
        }
        return {
            "call_connection_id": call_connection_id,
            "status": "connecting",
            "caller_id": caller_id,
        }

    def handle_call_event(
        self,
        event_type: str,
        event_data: dict,
    ) -> dict:
        """Return a deterministic mock event response."""
        short_type = event_type.split(".")[-1] if "." in event_type else event_type
        call_connection_id = (
            event_data.get("callConnectionId")
            or event_data.get("call_connection_id")
            or "mock-call-unknown"
        )

        if short_type == "CallConnected":
            return {
                "action": "call_connected",
                "call_connection_id": call_connection_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        elif short_type == "CallDisconnected":
            return {
                "action": "call_disconnected",
                "call_connection_id": call_connection_id,
                "ended_at": datetime.now(timezone.utc).isoformat(),
            }
        elif short_type == "MediaStreamingStarted":
            return {"action": "media_streaming_started", "call_connection_id": call_connection_id}
        elif short_type == "MediaStreamingStopped":
            return {"action": "media_streaming_stopped", "call_connection_id": call_connection_id}
        else:
            return {
                "action": "unhandled",
                "event_type": short_type,
                "call_connection_id": call_connection_id,
            }

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check — always healthy."""
        return True, 0, None

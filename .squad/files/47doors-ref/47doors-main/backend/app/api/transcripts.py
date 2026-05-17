"""SSE endpoint for streaming phone call transcripts to the frontend."""

import asyncio
import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.services.transcript_bus import transcript_bus

logger = logging.getLogger(__name__)

router = APIRouter()


async def _event_generator(request: Request):
    """Yield SSE-formatted transcript events until the client disconnects."""
    async with transcript_bus.subscribe() as queue:
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive comment to prevent proxy/browser timeout
                yield ": keepalive\n\n"


@router.get("/transcripts/stream")
async def stream_transcripts(request: Request) -> StreamingResponse:
    """Server-Sent Events stream of live phone call transcripts.

    Returns ``text/event-stream`` with JSON event payloads matching the
    shared API contract (call_started, user_speech, agent_speech,
    tool_call, call_ended).
    """
    return StreamingResponse(
        _event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

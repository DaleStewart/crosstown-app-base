"""Voice Realtime API endpoints."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.core.dependencies import get_realtime_service
from app.models.voice_schemas import (
    RealtimeSessionRequest,
    RealtimeSessionResponse,
    ToolCallRequest,
    ToolCallResponse,
)
from app.services.interfaces import RealtimeServiceInterface

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_realtime_service() -> RealtimeServiceInterface:
    """Wrapper avoids FastAPI interpreting Settings as a body sub-dependency."""
    return get_realtime_service()


@router.post("/session", response_model=RealtimeSessionResponse)
async def create_realtime_session(
    request: RealtimeSessionRequest,
    realtime_service: RealtimeServiceInterface = Depends(_resolve_realtime_service),
):
    """Create an ephemeral realtime session with a short-lived token.

    Returns session credentials for WebRTC connection to Azure OpenAI Realtime API.
    Token TTL ≤60 seconds per Constitution Principle III.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        response = await realtime_service.create_session(
            session_id=session_id,
            voice=request.voice,
            instructions=request.instructions,
        )
        return response
    except Exception as e:
        if "VoiceUnavailable" in type(e).__name__:
            logger.warning(f"Realtime API unavailable: {e}")
            raise HTTPException(
                status_code=503,
                detail={"error": "voice_unavailable", "message": str(e)},
            )
        raise


@router.websocket("/ws")
async def websocket_tool_relay(
    websocket: WebSocket,
    session_id: str = Query(...),
    token: str = Query(...),
):
    """WebSocket relay for Realtime API tool calls.

    Receives tool_call_request frames, executes through pipeline,
    returns tool_call_response frames. Audio goes direct via WebRTC.

    Close codes:
    - 1000: Normal closure
    - 4001: Invalid token
    - 4002: Session not found
    - 1011: Server error
    """
    realtime_service = _resolve_realtime_service()

    if not token or len(token) < 10:
        await websocket.accept()
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id}")

    try:
        while True:
            data = await websocket.receive_json()

            try:
                tool_request = ToolCallRequest(
                    call_id=data.get("call_id", ""),
                    tool_name=data.get("tool_name", ""),
                    arguments=data.get("arguments", {}),
                )
            except Exception as e:
                await websocket.send_json({
                    "call_id": data.get("call_id", "unknown"),
                    "result": "",
                    "error": f"Invalid request: {e}",
                })
                continue

            try:
                response = await realtime_service.execute_tool(
                    call_id=tool_request.call_id,
                    tool_name=tool_request.tool_name,
                    arguments=tool_request.arguments,
                    session_id=session_id,
                )
                await websocket.send_json(response.model_dump())
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                await websocket.send_json({
                    "call_id": tool_request.call_id,
                    "result": "",
                    "error": str(e),
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session={session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Server error")
        except Exception:
            pass


@router.get("/health")
async def realtime_health():
    """Check realtime API availability."""
    from app.core.dependencies import get_settings

    settings = get_settings()
    return {
        "realtime_available": settings.voice_enabled,
        "mock_mode": settings.mock_mode,
        "voice_enabled": settings.voice_enabled,
    }

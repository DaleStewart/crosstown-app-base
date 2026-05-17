"""Phone call automation endpoints (ACS Call Automation webhooks)."""

import inspect
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.dependencies import get_phone_service, get_settings
from app.models.phone_schemas import PhoneHealthResponse
from app.services.interfaces import PhoneServiceInterface

settings = get_settings()

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_phone_service() -> PhoneServiceInterface:
    """Wrapper avoids FastAPI interpreting Settings as a body sub-dependency."""
    return get_phone_service()


async def _call(method, *args, **kwargs):
    """Invoke a service method that may be sync or async."""
    result = method(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


@router.post("/incoming")
async def handle_incoming_call(request: Request) -> JSONResponse:
    """Event Grid webhook for ACS IncomingCall events.

    Handles two Event Grid request types:
    - SubscriptionValidation: echo back validationCode to confirm subscription
    - IncomingCall: answer the call and bridge to the AI agent

    ACS delivers a JSON array; each item has an 'eventType' property.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    events = body if isinstance(body, list) else [body]
    if not events:
        raise HTTPException(status_code=400, detail="Empty event array")

    # Process the first event in the batch
    event = events[0]
    event_type = event.get("eventType") or event.get("type", "")

    # Event Grid subscription validation handshake (both event type variants)
    if event_type in (
        "Microsoft.EventGrid.SubscriptionValidationEvent",
        "Microsoft.EventGrid.SubscriptionValidated",
    ):
        data = event.get("data", {})
        validation_code = data.get("validationCode", "")
        logger.info("Phone: Event Grid subscription validation handshake")
        return JSONResponse(content={"validationResponse": validation_code})

    # Incoming PSTN call
    if event_type == "Microsoft.Communication.IncomingCall":
        data = event.get("data", {})
        incoming_call_context = data.get("incomingCallContext", "")
        caller_raw = data.get("from", {})
        # ACS nests the caller number under from.rawId or from.phoneNumber.value
        if isinstance(caller_raw, dict):
            caller_id = (
                caller_raw.get("rawId")
                or caller_raw.get("phoneNumber", {}).get("value", "unknown")
            )
        else:
            caller_id = str(caller_raw) if caller_raw else "unknown"

        if not incoming_call_context:
            logger.warning("Phone: IncomingCall event missing incomingCallContext")
            return JSONResponse(content={"status": "skipped", "reason": "missing_context"})

        # ACS requires a publicly-reachable HTTPS callback URL.
        # Container Apps terminate TLS at the ingress, so request.base_url
        # yields an internal http:// URL.  Prefer the explicit config; fall
        # back to reconstructing from forwarded headers.
        if settings.phone_callback_base_url:
            base = settings.phone_callback_base_url.rstrip("/")
        else:
            scheme = request.headers.get("x-forwarded-proto", "https")
            host = (
                request.headers.get("x-forwarded-host")
                or request.headers.get("host")
                or ""
            )
            base = f"{scheme}://{host}" if host else str(request.base_url).rstrip("/")
        callback_url = f"{base}/api/phone/callbacks"
        logger.info(f"Phone: using callback URL: {callback_url}")

        phone_service = _resolve_phone_service()
        try:
            result = await _call(
                phone_service.handle_incoming_call,
                incoming_call_context=incoming_call_context,
                caller_id=caller_id,
                callback_url=callback_url,
            )
            logger.info(f"Phone: call answered, connection_id={result.get('call_connection_id')}")
            return JSONResponse(content=result)
        except Exception as exc:
            if "PhoneUnavailable" in type(exc).__name__:
                logger.warning(f"Phone: service unavailable: {exc}")
                raise HTTPException(
                    status_code=503,
                    detail={"error": "phone_unavailable", "message": str(exc)},
                )
            logger.error(f"Phone: unexpected error handling IncomingCall: {exc}")
            raise

    # Unknown event type — log and acknowledge to prevent Event Grid retries
    logger.debug(f"Phone: unhandled Event Grid event type: {event_type}")
    return JSONResponse(content={"status": "unhandled", "event_type": event_type})


@router.post("/callbacks")
async def handle_call_callbacks(request: Request) -> JSONResponse:
    """Call Automation callback endpoint.

    ACS POSTs CloudEvent arrays here as calls progress through their lifecycle.
    Each event carries a type and a data payload with the call_connection_id.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # Normalise: single object or array
    events = body if isinstance(body, list) else [body]

    # Validate: require at least one event with both event type and connection id
    if not events:
        raise HTTPException(status_code=400, detail="Empty event payload")

    results: list[Any] = []
    phone_service = _resolve_phone_service()

    for event in events:
        # ACS Call Automation sends CloudEvents: type at top, payload in "data".
        # Also support flat format for backward compatibility.
        event_type = (
            event.get("type")
            or event.get("eventType")
            or event.get("event_type")
            or ""
        )

        # CloudEvents nests payload in "data"; flat format has fields at top level
        data = event.get("data", event)

        call_connection_id = (
            data.get("callConnectionId")
            or data.get("call_connection_id")
            or event.get("callConnectionId")
            or event.get("call_connection_id")
            or ""
        )

        if not event_type:
            logger.warning(f"Phone callback: missing event_type, keys={list(event.keys())}")
            results.append({"error": "missing_event_type"})
            continue
        if not call_connection_id:
            logger.warning(
                f"Phone callback: missing call_connection_id for {event_type}, "
                f"data_keys={list(data.keys())}"
            )
            results.append({"error": "missing_call_connection_id", "event_type": event_type})
            continue

        # Pass the inner data dict (not the CloudEvents envelope) to the service
        event_data = {
            **data,
            "callConnectionId": call_connection_id,
        }

        try:
            result = await _call(
                phone_service.handle_call_event,
                event_type=event_type,
                event_data=event_data,
            )
            results.append(result)
        except Exception as exc:
            logger.error(f"Phone: error handling callback event {event_type}: {exc}")
            results.append({"error": str(exc), "event_type": event_type})

    return JSONResponse(content={"processed": len(results), "results": results})


@router.get("/health", response_model=PhoneHealthResponse)
async def phone_health() -> PhoneHealthResponse:
    """Check phone service availability."""
    settings = get_settings()
    phone_service = _resolve_phone_service()

    result = await _call(phone_service.health_check)
    is_healthy, latency_ms, error = result

    return PhoneHealthResponse(
        phone_available=is_healthy and settings.phone_enabled,
        mock_mode=settings.mock_mode,
        phone_enabled=settings.phone_enabled,
        latency_ms=latency_ms,
        error=error,
    )

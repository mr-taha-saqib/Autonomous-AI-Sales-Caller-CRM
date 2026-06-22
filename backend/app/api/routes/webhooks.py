"""Twilio webhook handlers — the live AI conversation loop.

These endpoints are called by Twilio (not the dashboard) and return TwiML. They are
authenticated via Twilio request signature validation instead of JWT.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Query, Request, Response
from sqlalchemy.orm import Session
from twilio.request_validator import RequestValidator

from app.core.config import settings
from app.core.logging import get_logger
from app.models.call import Call, CallStatus
from app.core.database import get_db
from app.services import conversation, twilio_service
from app.services.prompts import OPENING_LINE, OPENING_LINE_NO_NAME

log = get_logger("webhooks")
router = APIRouter(prefix="/webhooks/twilio", tags=["webhooks"])

_TWILIO_STATUS_MAP = {
    "queued": CallStatus.QUEUED,
    "initiated": CallStatus.INITIATED,
    "ringing": CallStatus.RINGING,
    "in-progress": CallStatus.IN_PROGRESS,
    "completed": CallStatus.COMPLETED,
    "busy": CallStatus.BUSY,
    "no-answer": CallStatus.NO_ANSWER,
    "failed": CallStatus.FAILED,
    "canceled": CallStatus.CANCELED,
}


async def _validate_twilio(request: Request) -> bool:
    """Validate the X-Twilio-Signature header. Skipped when no auth token set."""
    if not settings.TWILIO_AUTH_TOKEN:
        return True
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    form = await request.form()
    url = str(request.url)
    return validator.validate(url, dict(form), signature)


def _twiml(vr) -> Response:
    return Response(content=str(vr), media_type="application/xml")


@router.post("/voice")
async def voice_entrypoint(
    request: Request,
    call_id: int = Query(...),
    reprompt: int = Query(0),
    db: Session = Depends(get_db),
):
    """First TwiML hit when the call connects. Speaks the opening line."""
    if not await _validate_twilio(request):
        return Response(status_code=403)

    call = db.get(Call, call_id)
    if not call:
        return _twiml(twilio_service.hangup("Sorry, an error occurred. Goodbye."))

    call.status = CallStatus.IN_PROGRESS
    db.add(call)

    if reprompt:
        opening = "Sorry, I didn't catch that. Are you still there?"
    elif call.lead and call.lead.full_name:
        opening = OPENING_LINE.format(name=call.lead.full_name)
    else:
        opening = OPENING_LINE_NO_NAME

    # Seed the transcript with the assistant's opening turn.
    conversation._get_or_create_transcript(db, call)
    t = call.transcript
    turns = list(t.turns or [])
    if not turns:
        turns.append({"role": "assistant", "text": opening, "ts": 0})
        t.turns = turns
        db.add(t)

    return _twiml(twilio_service.gather_speech(call_id=call_id, prompt=opening))


@router.post("/gather")
async def gather_handler(
    request: Request,
    call_id: int = Query(...),
    SpeechResult: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Called after each customer utterance. Drives the AI conversation."""
    if not await _validate_twilio(request):
        return Response(status_code=403)

    call = db.get(Call, call_id)
    if not call:
        return _twiml(twilio_service.hangup("Goodbye."))

    customer_text = (SpeechResult or "").strip()
    reply, should_hangup = conversation.next_turn(db, call, customer_text or None)

    if should_hangup:
        return _twiml(twilio_service.hangup(reply))
    return _twiml(twilio_service.gather_speech(call_id=call_id, prompt=reply))


@router.post("/status")
async def status_callback(
    request: Request,
    call_id: int = Query(...),
    CallStatus: str = Form(default=""),
    CallDuration: str = Form(default="0"),
    db: Session = Depends(get_db),
):
    """Twilio call lifecycle events. Finalises the call when completed."""
    if not await _validate_twilio(request):
        return Response(status_code=403)

    call = db.get(Call, call_id)
    if not call:
        return Response(status_code=204)

    mapped = _TWILIO_STATUS_MAP.get(CallStatus.lower())
    if mapped:
        call.status = mapped
    try:
        call.duration_seconds = int(CallDuration or 0)
    except ValueError:
        pass

    if mapped == _TWILIO_STATUS_MAP["completed"]:
        conversation.finalize_call(db, call)

    db.add(call)
    log.info("call_status", call_id=call_id, status=CallStatus)
    return Response(status_code=204)


@router.post("/recording")
async def recording_callback(
    request: Request,
    call_id: int = Query(...),
    RecordingUrl: str = Form(default=""),
    db: Session = Depends(get_db),
):
    if not await _validate_twilio(request):
        return Response(status_code=403)
    call = db.get(Call, call_id)
    if call and RecordingUrl:
        call.recording_url = RecordingUrl
        db.add(call)
    return Response(status_code=204)


@router.post("/inbound")
async def inbound_call(
    request: Request,
    From: str = Form(default=""),
    To: str = Form(default=""),
    CallSid: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """Entry point for inbound calls to the Algorixe number."""
    if not await _validate_twilio(request):
        return Response(status_code=403)

    call = Call(
        twilio_sid=CallSid,
        direction="inbound",
        status=CallStatus.IN_PROGRESS,
        from_number=From,
        to_number=To,
    )
    db.add(call)
    db.flush()
    greeting = (
        "Thank you for calling Algorixe Car Care. "
        "This is the Algorixe Sales Assistant. How can I help you today?"
    )
    conversation._get_or_create_transcript(db, call)
    call.transcript.turns = [{"role": "assistant", "text": greeting, "ts": 0}]
    db.add(call.transcript)
    return _twiml(twilio_service.gather_speech(call_id=call.id, prompt=greeting))

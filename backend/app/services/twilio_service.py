"""Twilio Voice integration — place calls and build TwiML responses.

Conversation flow uses Twilio <Gather input="speech"> for speech-to-text and
<Say> (Amazon Polly Neural) for text-to-speech, looping back to our webhook on
each customer utterance. This keeps the whole call server-driven and recordable
without managing raw media streams.
"""
from __future__ import annotations

from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

from app.core.config import settings
from app.core.logging import get_logger

log = get_logger("twilio")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _client


def place_outbound_call(to_number: str, call_db_id: int) -> str:
    """Start an outbound call. Returns the Twilio Call SID."""
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    call = get_client().calls.create(
        to=to_number,
        from_=settings.TWILIO_CALLER_ID,
        url=f"{base}/api/v1/webhooks/twilio/voice?call_id={call_db_id}",
        status_callback=f"{base}/api/v1/webhooks/twilio/status?call_id={call_db_id}",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
        status_callback_method="POST",
        record=True,
        recording_status_callback=(
            f"{base}/api/v1/webhooks/twilio/recording?call_id={call_db_id}"
        ),
        machine_detection="DetectMessageEnd",
    )
    log.info("outbound_call_placed", sid=call.sid, to=to_number)
    return call.sid


def say(response: VoiceResponse, text: str) -> None:
    response.say(text, voice=settings.TWILIO_VOICE)


def gather_speech(
    *, call_id: int, prompt: str, timeout: int = 4, speech_timeout: str = "auto"
) -> VoiceResponse:
    """Build a TwiML response that speaks `prompt` then listens for the reply."""
    base = settings.PUBLIC_BASE_URL.rstrip("/")
    vr = VoiceResponse()
    gather = Gather(
        input="speech",
        action=f"{base}/api/v1/webhooks/twilio/gather?call_id={call_id}",
        method="POST",
        timeout=timeout,
        speech_timeout=speech_timeout,
        speech_model="phone_call",
        language="en-US",
        action_on_empty_result=True,
    )
    gather.say(prompt, voice=settings.TWILIO_VOICE)
    vr.append(gather)
    # If no speech detected, gently re-prompt once by redirecting back.
    vr.redirect(
        f"{base}/api/v1/webhooks/twilio/voice?call_id={call_id}&reprompt=1",
        method="POST",
    )
    return vr


def hangup(text: str | None = None) -> VoiceResponse:
    vr = VoiceResponse()
    if text:
        vr.say(text, voice=settings.TWILIO_VOICE)
    vr.hangup()
    return vr

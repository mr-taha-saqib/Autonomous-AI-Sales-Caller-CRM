"""Conversation orchestrator — bridges Twilio webhooks, Claude and the CRM.

State (the running transcript) lives in the `transcripts` table keyed by call. Each
inbound webhook appends the customer turn, asks Claude for the next reply, appends it,
and returns TwiML that speaks the reply and gathers the next utterance.
"""
from __future__ import annotations

import time

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.call import Call, CallStatus
from app.models.lead import Lead, LeadStatus
from app.models.transcript import Transcript
from app.services import claude_service
from app.services.lead_scoring import score_lead

log = get_logger("conversation")

# Heuristic end-of-call signals from the assistant's reply.
_FAREWELL_HINTS = (
    "thank you for your time",
    "have a great day",
    "take care",
    "goodbye",
    "we'll be in touch",
)


def _get_or_create_transcript(db: Session, call: Call) -> Transcript:
    if call.transcript:
        return call.transcript
    t = Transcript(call_id=call.id, turns=[])
    db.add(t)
    db.flush()
    call.transcript = t
    return t


def _build_lead_context(call: Call) -> str:
    if not call.lead:
        return ""
    lead = call.lead
    parts = []
    if lead.full_name:
        parts.append(f"name={lead.full_name}")
    if lead.vehicle_interest:
        parts.append(f"interested_in={lead.vehicle_interest}")
    if lead.budget:
        parts.append(f"budget={lead.budget}")
    return ", ".join(parts)


def next_turn(db: Session, call: Call, customer_text: str | None) -> tuple[str, bool]:
    """Advance the conversation. Returns (assistant_reply, should_hangup)."""
    transcript = _get_or_create_transcript(db, call)
    turns: list[dict] = list(transcript.turns or [])

    if customer_text:
        turns.append({"role": "user", "text": customer_text, "ts": time.time()})

    # Build Claude message history from turns.
    history = [
        {"role": t["role"], "content": t["text"]}
        for t in turns
        if t.get("text")
    ]

    reply = claude_service.generate_reply(history, _build_lead_context(call))
    turns.append({"role": "assistant", "text": reply, "ts": time.time()})

    transcript.turns = turns
    transcript.full_text = claude_service.transcript_to_text(turns)
    db.add(transcript)

    should_hangup = any(h in reply.lower() for h in _FAREWELL_HINTS)
    return reply, should_hangup


def finalize_call(db: Session, call: Call) -> None:
    """Run extraction + summarisation and update lead scoring after a call ends."""
    transcript = call.transcript
    if not transcript or not transcript.turns:
        call.outcome = "no_answer"
        return

    text = transcript.full_text or claude_service.transcript_to_text(transcript.turns)

    summary = claude_service.summarise_call(text)
    transcript.summary = summary.get("summary")
    transcript.key_intent = summary.get("key_intent")
    transcript.sentiment = summary.get("sentiment")
    transcript.outcome = summary.get("outcome")

    call.summary = summary.get("summary")
    call.key_intent = summary.get("key_intent")
    call.sentiment = summary.get("sentiment")
    call.outcome = summary.get("outcome")

    fields = claude_service.extract_lead_fields(text)
    _upsert_lead_from_extraction(db, call, fields, summary.get("sentiment"))
    db.add(transcript)
    db.add(call)
    log.info("call_finalized", call_id=call.id, outcome=call.outcome)


def _upsert_lead_from_extraction(
    db: Session, call: Call, fields: dict, sentiment: str | None
) -> None:
    lead = call.lead
    if lead is None:
        lead = Lead(phone=call.to_number, source="outbound_call")
        db.add(lead)
        db.flush()
        call.lead_id = lead.id

    for attr in (
        "full_name", "email", "location", "budget",
        "vehicle_interest", "purchase_timeline",
        "financing_need", "trade_in_interest",
    ):
        value = fields.get(attr)
        if value not in (None, ""):
            setattr(lead, attr, value)

    score, temperature, probability = score_lead(
        purchase_timeline=lead.purchase_timeline,
        budget=lead.budget,
        vehicle_interest=lead.vehicle_interest,
        financing_need=lead.financing_need,
        trade_in_interest=lead.trade_in_interest,
        email=lead.email,
        sentiment=sentiment,
    )
    lead.score = score
    lead.temperature = temperature
    lead.conversion_probability = probability
    lead.sentiment = sentiment
    lead.intent_summary = call.key_intent

    if call.outcome == "appointment_booked":
        lead.status = LeadStatus.APPOINTMENT_SET
    elif call.outcome == "do_not_call":
        lead.status = LeadStatus.DO_NOT_CALL
    elif call.outcome in ("qualified", "needs_followup", "callback_requested"):
        lead.status = LeadStatus.QUALIFIED
    elif call.outcome == "not_interested":
        lead.status = LeadStatus.LOST
    elif lead.status == LeadStatus.NEW:
        lead.status = LeadStatus.CONTACTED

    db.add(lead)

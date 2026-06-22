from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.call import CallDirection, CallStatus


class OutboundCallRequest(BaseModel):
    to_number: str = Field(min_length=7, max_length=32, examples=["+15558675309"])
    lead_id: int | None = None
    campaign: str | None = None


class TranscriptOut(BaseModel):
    id: int
    turns: list
    full_text: str | None = None
    summary: str | None = None
    key_intent: str | None = None
    sentiment: str | None = None
    outcome: str | None = None

    model_config = {"from_attributes": True}


class CallOut(BaseModel):
    id: int
    twilio_sid: str | None = None
    direction: CallDirection
    status: CallStatus
    from_number: str
    to_number: str
    duration_seconds: int
    recording_url: str | None = None
    summary: str | None = None
    key_intent: str | None = None
    sentiment: str | None = None
    outcome: str | None = None
    lead_id: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CallDetail(CallOut):
    transcript: TranscriptOut | None = None


class CallList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[CallOut]

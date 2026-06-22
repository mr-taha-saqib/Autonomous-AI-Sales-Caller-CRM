"""Call record — one row per Twilio call."""
from __future__ import annotations

import enum

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, enum_column


class CallDirection(str, enum.Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class CallStatus(str, enum.Enum):
    QUEUED = "queued"
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    FAILED = "failed"
    CANCELED = "canceled"
    VOICEMAIL = "voicemail"


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    twilio_sid: Mapped[str | None] = mapped_column(
        String(64), unique=True, index=True
    )
    direction: Mapped[CallDirection] = mapped_column(
        enum_column(CallDirection, "call_direction"), nullable=False
    )
    status: Mapped[CallStatus] = mapped_column(
        enum_column(CallStatus, "call_status"),
        default=CallStatus.QUEUED,
        nullable=False,
        index=True,
    )
    from_number: Mapped[str] = mapped_column(String(32), nullable=False)
    to_number: Mapped[str] = mapped_column(String(32), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    recording_url: Mapped[str | None] = mapped_column(String(512))

    # AI-derived fields
    summary: Mapped[str | None] = mapped_column(Text)
    key_intent: Mapped[str | None] = mapped_column(String(255))
    sentiment: Mapped[str | None] = mapped_column(String(20))
    outcome: Mapped[str | None] = mapped_column(String(60))

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    lead_id: Mapped[int | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"), index=True
    )

    customer = relationship("Customer", back_populates="calls")
    lead = relationship("Lead", back_populates="calls")
    transcript = relationship(
        "Transcript", back_populates="call", uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Call {self.twilio_sid} {self.direction}/{self.status}>"

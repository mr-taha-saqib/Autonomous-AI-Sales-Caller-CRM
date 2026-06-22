"""Call transcript storage — full conversation plus AI analysis."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, JSONVariant


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(
        ForeignKey("calls.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Full ordered conversation as JSON: [{"role": "...", "text": "...", "ts": ...}]
    turns: Mapped[list] = mapped_column(JSONVariant, default=list, nullable=False)
    full_text: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    key_intent: Mapped[str | None] = mapped_column(String(255))
    sentiment: Mapped[str | None] = mapped_column(String(20))
    outcome: Mapped[str | None] = mapped_column(String(60))

    call = relationship("Call", back_populates="transcript")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Transcript call={self.call_id} turns={len(self.turns or [])}>"


# Convenience structure used in services (not a table)
class TranscriptTurn(dict):
    """A single {role, text, ts} turn. Subclassing dict keeps JSONB simple."""

    @classmethod
    def make(cls, role: str, text: str, ts: float | None = None) -> "TranscriptTurn":
        return cls(role=role, text=text, ts=ts)

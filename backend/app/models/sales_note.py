"""Free-form sales notes attached to a lead."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SalesNote(Base):
    __tablename__ = "sales_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False
    )
    author_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    category: Mapped[str] = mapped_column(String(40), default="general")
    body: Mapped[str] = mapped_column(Text, nullable=False)

    lead = relationship("Lead", back_populates="notes")
    author = relationship("User", back_populates="sales_notes")

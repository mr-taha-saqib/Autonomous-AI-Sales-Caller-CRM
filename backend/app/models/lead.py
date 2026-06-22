"""Sales lead with qualification data and temperature scoring."""
from __future__ import annotations

import enum

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, enum_column


class LeadTemperature(str, enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    APPOINTMENT_SET = "appointment_set"
    CONVERTED = "converted"
    LOST = "lost"
    DO_NOT_CALL = "do_not_call"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )

    # Captured qualification fields
    full_name: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(160))
    budget: Mapped[str | None] = mapped_column(String(80))
    vehicle_interest: Mapped[str | None] = mapped_column(String(160))
    purchase_timeline: Mapped[str | None] = mapped_column(String(80))
    financing_need: Mapped[bool | None] = mapped_column()
    trade_in_interest: Mapped[bool | None] = mapped_column()

    # Scoring
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    temperature: Mapped[LeadTemperature] = mapped_column(
        enum_column(LeadTemperature, "lead_temperature"),
        default=LeadTemperature.COLD,
        nullable=False,
    )
    status: Mapped[LeadStatus] = mapped_column(
        enum_column(LeadStatus, "lead_status"),
        default=LeadStatus.NEW,
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(60), default="outbound_call")
    intent_summary: Mapped[str | None] = mapped_column(Text)
    sentiment: Mapped[str | None] = mapped_column(String(20))
    conversion_probability: Mapped[float | None] = mapped_column(Float)

    customer = relationship("Customer", back_populates="leads")
    calls = relationship("Call", back_populates="lead")
    appointments = relationship("Appointment", back_populates="lead")
    notes = relationship("SalesNote", back_populates="lead")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Lead {self.phone} {self.temperature}/{self.status}>"

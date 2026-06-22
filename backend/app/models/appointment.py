"""Appointments — showroom visits and virtual consultations."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, enum_column


class AppointmentType(str, enum.Enum):
    SHOWROOM_VISIT = "showroom_visit"
    VIRTUAL_CONSULTATION = "virtual_consultation"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id", ondelete="SET NULL"), index=True
    )
    lead_id: Mapped[int | None] = mapped_column(
        ForeignKey("leads.id", ondelete="SET NULL"), index=True
    )
    sales_rep_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    appointment_type: Mapped[AppointmentType] = mapped_column(
        enum_column(AppointmentType, "appointment_type"),
        default=AppointmentType.SHOWROOM_VISIT,
        nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        enum_column(AppointmentStatus, "appointment_status"),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True,
    )
    scheduled_for: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    location: Mapped[str | None] = mapped_column(String(200))
    meeting_link: Mapped[str | None] = mapped_column(String(400))
    notes: Mapped[str | None] = mapped_column(Text)

    customer = relationship("Customer", back_populates="appointments")
    lead = relationship("Lead", back_populates="appointments")
    sales_rep = relationship("User", back_populates="appointments")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Appointment {self.scheduled_for} {self.status}>"

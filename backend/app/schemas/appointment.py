from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.appointment import AppointmentStatus, AppointmentType


class AppointmentCreate(BaseModel):
    lead_id: int | None = None
    customer_id: int | None = None
    sales_rep_id: int | None = None
    appointment_type: AppointmentType = AppointmentType.SHOWROOM_VISIT
    scheduled_for: datetime
    location: str | None = None
    meeting_link: str | None = None
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    sales_rep_id: int | None = None
    appointment_type: AppointmentType | None = None
    status: AppointmentStatus | None = None
    scheduled_for: datetime | None = None
    location: str | None = None
    meeting_link: str | None = None
    notes: str | None = None


class AppointmentOut(BaseModel):
    id: int
    lead_id: int | None = None
    customer_id: int | None = None
    sales_rep_id: int | None = None
    appointment_type: AppointmentType
    status: AppointmentStatus
    scheduled_for: datetime
    location: str | None = None
    meeting_link: str | None = None
    notes: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}

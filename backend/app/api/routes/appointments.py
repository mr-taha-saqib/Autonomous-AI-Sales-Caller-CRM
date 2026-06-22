"""Appointment scheduling — showroom visits & virtual consultations."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_agent
from app.core.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.lead import Lead, LeadStatus
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
)
from app.schemas.common import Message
from app.services.audit import log_activity

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentOut])
def list_appointments(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    status: AppointmentStatus | None = None,
    sales_rep_id: int | None = None,
    upcoming: bool = Query(False),
):
    q = db.query(Appointment)
    if status:
        q = q.filter(Appointment.status == status)
    if sales_rep_id:
        q = q.filter(Appointment.sales_rep_id == sales_rep_id)
    if upcoming:
        q = q.filter(Appointment.scheduled_for >= datetime.utcnow())
    return q.order_by(Appointment.scheduled_for.asc()).all()


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(
    body: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    appt = Appointment(**body.model_dump())
    db.add(appt)
    db.flush()

    if body.lead_id:
        lead = db.get(Lead, body.lead_id)
        if lead:
            lead.status = LeadStatus.APPOINTMENT_SET
            db.add(lead)

    log_activity(db, user_id=user.id, action="appointment_created",
                 entity_type="appointment", entity_id=appt.id)
    return appt


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    body: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(appt, k, v)
    db.add(appt)
    log_activity(db, user_id=user.id, action="appointment_updated",
                 entity_type="appointment", entity_id=appt.id)
    return appt


@router.delete("/{appointment_id}", response_model=Message)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    appt = db.get(Appointment, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt.status = AppointmentStatus.CANCELED
    db.add(appt)
    log_activity(db, user_id=user.id, action="appointment_canceled",
                 entity_type="appointment", entity_id=appt.id)
    return Message(detail="Appointment canceled")

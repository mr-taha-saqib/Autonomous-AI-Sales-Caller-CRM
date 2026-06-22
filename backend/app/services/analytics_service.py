"""Analytics & reporting — aggregates CRM data into dashboard metrics."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, AppointmentStatus
from app.models.call import Call, CallStatus
from app.models.lead import Lead, LeadStatus, LeadTemperature


def _rate(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 2) if denominator else 0.0


def dashboard_summary(db: Session) -> dict:
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    hot = db.query(func.count(Lead.id)).filter(
        Lead.temperature == LeadTemperature.HOT).scalar() or 0
    warm = db.query(func.count(Lead.id)).filter(
        Lead.temperature == LeadTemperature.WARM).scalar() or 0
    cold = db.query(func.count(Lead.id)).filter(
        Lead.temperature == LeadTemperature.COLD).scalar() or 0
    converted = db.query(func.count(Lead.id)).filter(
        Lead.status == LeadStatus.CONVERTED).scalar() or 0

    total_calls = db.query(func.count(Call.id)).scalar() or 0
    completed_calls = db.query(func.count(Call.id)).filter(
        Call.status == CallStatus.COMPLETED).scalar() or 0
    avg_duration = db.query(func.avg(Call.duration_seconds)).filter(
        Call.status == CallStatus.COMPLETED).scalar() or 0

    appts_scheduled = db.query(func.count(Appointment.id)).scalar() or 0
    appts_completed = db.query(func.count(Appointment.id)).filter(
        Appointment.status == AppointmentStatus.COMPLETED).scalar() or 0

    return {
        "total_leads": total_leads,
        "hot_leads": hot,
        "warm_leads": warm,
        "cold_leads": cold,
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "appointments_scheduled": appts_scheduled,
        "appointments_completed": appts_completed,
        "lead_conversion_rate": _rate(converted, total_leads),
        "appointment_conversion_rate": _rate(appts_completed, appts_scheduled),
        "avg_call_duration_seconds": round(float(avg_duration), 1),
    }


def sales_funnel(db: Session) -> list[dict]:
    stages = [
        ("New", LeadStatus.NEW),
        ("Contacted", LeadStatus.CONTACTED),
        ("Qualified", LeadStatus.QUALIFIED),
        ("Appointment Set", LeadStatus.APPOINTMENT_SET),
        ("Converted", LeadStatus.CONVERTED),
    ]
    out = []
    for label, status in stages:
        count = db.query(func.count(Lead.id)).filter(
            Lead.status == status).scalar() or 0
        out.append({"stage": label, "count": count})
    return out


def _timeseries(db: Session, model, days: int) -> list[dict]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(model.created_at).label("d"),
            func.count(model.id).label("c"),
        )
        .filter(model.created_at >= since)
        .group_by(func.date(model.created_at))
        .order_by(func.date(model.created_at))
        .all()
    )
    return [{"date": str(r.d), "value": float(r.c)} for r in rows]


def report(db: Session, period: str) -> dict:
    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return {
        "period": period,
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "summary": dashboard_summary(db),
        "funnel": sales_funnel(db),
        "calls_by_day": _timeseries(db, Call, days),
        "leads_by_day": _timeseries(db, Lead, days),
    }

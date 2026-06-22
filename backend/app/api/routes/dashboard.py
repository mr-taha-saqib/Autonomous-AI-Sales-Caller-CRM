"""Dashboard aggregation endpoints — recent activity feed for the home screen."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.activity_log import ActivityLog
from app.models.appointment import Appointment
from app.models.call import Call
from app.models.lead import Lead
from app.models.user import User
from app.services import analytics_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/home")
def home(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    summary = analytics_service.dashboard_summary(db)
    recent_calls = (
        db.query(Call).order_by(Call.created_at.desc()).limit(8).all()
    )
    hot_leads = (
        db.query(Lead).order_by(Lead.score.desc()).limit(8).all()
    )
    upcoming = (
        db.query(Appointment)
        .order_by(Appointment.scheduled_for.asc())
        .limit(8)
        .all()
    )
    activity = (
        db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(15).all()
    )
    return {
        "summary": summary,
        "funnel": analytics_service.sales_funnel(db),
        "recent_calls": [
            {
                "id": c.id, "to_number": c.to_number, "status": c.status.value,
                "outcome": c.outcome, "created_at": c.created_at.isoformat(),
            }
            for c in recent_calls
        ],
        "hot_leads": [
            {
                "id": l.id, "full_name": l.full_name, "phone": l.phone,
                "score": l.score, "temperature": l.temperature.value,
                "vehicle_interest": l.vehicle_interest,
            }
            for l in hot_leads
        ],
        "upcoming_appointments": [
            {
                "id": a.id, "type": a.appointment_type.value,
                "scheduled_for": a.scheduled_for.isoformat(),
                "status": a.status.value,
            }
            for a in upcoming
        ],
        "recent_activity": [
            {
                "action": a.action, "entity": a.entity_type,
                "created_at": a.created_at.isoformat(),
            }
            for a in activity
        ],
    }

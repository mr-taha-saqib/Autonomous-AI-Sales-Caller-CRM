"""SQLAlchemy ORM models for the Algorixe CRM."""
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.lead import Lead, LeadStatus, LeadTemperature
from app.models.call import Call, CallDirection, CallStatus
from app.models.transcript import Transcript, TranscriptTurn
from app.models.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.models.sales_note import SalesNote
from app.models.activity_log import ActivityLog

__all__ = [
    "User",
    "UserRole",
    "Customer",
    "Lead",
    "LeadStatus",
    "LeadTemperature",
    "Call",
    "CallDirection",
    "CallStatus",
    "Transcript",
    "TranscriptTurn",
    "Appointment",
    "AppointmentStatus",
    "AppointmentType",
    "SalesNote",
    "ActivityLog",
]

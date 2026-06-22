"""Top-level API v1 router aggregating all route modules."""
from fastapi import APIRouter

from app.api.routes import (
    analytics,
    appointments,
    auth,
    calls,
    dashboard,
    leads,
    users,
    webhooks,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(leads.router)
api_router.include_router(calls.router)
api_router.include_router(appointments.router)
api_router.include_router(analytics.router)
api_router.include_router(dashboard.router)
api_router.include_router(webhooks.router)

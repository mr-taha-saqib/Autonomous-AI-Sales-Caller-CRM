"""Audit logging helper."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    ip_address: str | None = None,
    detail: dict | None = None,
) -> None:
    db.add(
        ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            detail=detail,
        )
    )

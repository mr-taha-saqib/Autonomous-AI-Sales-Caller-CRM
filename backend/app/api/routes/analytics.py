"""Analytics, dashboard summary and reports."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_manager
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import DashboardSummary, ReportOut
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return analytics_service.dashboard_summary(db)


@router.get("/funnel")
def funnel(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return analytics_service.sales_funnel(db)


@router.get("/reports/{period}", response_model=ReportOut,
            dependencies=[Depends(require_manager)])
def reports(period: str, db: Session = Depends(get_db)):
    if period not in ("daily", "weekly", "monthly"):
        raise HTTPException(status_code=400, detail="period must be daily|weekly|monthly")
    return analytics_service.report(db, period)

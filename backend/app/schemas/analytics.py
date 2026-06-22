from __future__ import annotations

from pydantic import BaseModel


class FunnelStage(BaseModel):
    stage: str
    count: int


class TimeseriesPoint(BaseModel):
    date: str
    value: float


class DashboardSummary(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    total_calls: int
    completed_calls: int
    appointments_scheduled: int
    appointments_completed: int
    lead_conversion_rate: float
    appointment_conversion_rate: float
    avg_call_duration_seconds: float


class ReportOut(BaseModel):
    period: str            # daily | weekly | monthly
    start_date: str
    end_date: str
    summary: DashboardSummary
    funnel: list[FunnelStage]
    calls_by_day: list[TimeseriesPoint]
    leads_by_day: list[TimeseriesPoint]

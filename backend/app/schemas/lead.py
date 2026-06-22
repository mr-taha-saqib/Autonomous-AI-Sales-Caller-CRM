from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.lead import LeadStatus, LeadTemperature


class LeadBase(BaseModel):
    full_name: str | None = None
    phone: str = Field(min_length=7, max_length=32)
    email: EmailStr | None = None
    location: str | None = None
    budget: str | None = None
    vehicle_interest: str | None = None
    purchase_timeline: str | None = None
    financing_need: bool | None = None
    trade_in_interest: bool | None = None


class LeadCreate(LeadBase):
    source: str = "manual"


class LeadUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    location: str | None = None
    budget: str | None = None
    vehicle_interest: str | None = None
    purchase_timeline: str | None = None
    financing_need: bool | None = None
    trade_in_interest: bool | None = None
    status: LeadStatus | None = None
    intent_summary: str | None = None


class LeadOut(LeadBase):
    id: int
    score: int
    temperature: LeadTemperature
    status: LeadStatus
    source: str
    intent_summary: str | None = None
    sentiment: str | None = None
    conversion_probability: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[LeadOut]

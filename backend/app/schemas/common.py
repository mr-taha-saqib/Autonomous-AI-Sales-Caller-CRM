from __future__ import annotations

from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class HealthCheck(BaseModel):
    status: str
    version: str
    database: str
    environment: str


class SalesNoteCreate(BaseModel):
    lead_id: int
    category: str = "general"
    body: str


class SalesNoteOut(BaseModel):
    id: int
    lead_id: int
    author_id: int | None = None
    category: str
    body: str

    model_config = {"from_attributes": True}

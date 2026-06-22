"""Lead CRUD, filtering, scoring, and notes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_agent
from app.core.database import get_db
from app.models.lead import Lead, LeadStatus, LeadTemperature
from app.models.sales_note import SalesNote
from app.models.user import User
from app.schemas.common import SalesNoteCreate, SalesNoteOut
from app.schemas.lead import LeadCreate, LeadList, LeadOut, LeadUpdate
from app.services.audit import log_activity
from app.services.lead_scoring import score_lead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=LeadList)
def list_leads(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    temperature: LeadTemperature | None = None,
    status: LeadStatus | None = None,
    search: str | None = None,
):
    q = db.query(Lead)
    if temperature:
        q = q.filter(Lead.temperature == temperature)
    if status:
        q = q.filter(Lead.status == status)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Lead.full_name.ilike(like),
            Lead.phone.ilike(like),
            Lead.email.ilike(like),
            Lead.vehicle_interest.ilike(like),
        ))
    total = q.count()
    items = (
        q.order_by(Lead.score.desc(), Lead.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return LeadList(total=total, page=page, page_size=page_size, items=items)


@router.post("", response_model=LeadOut, status_code=201)
def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    lead = Lead(**body.model_dump())
    score, temp, prob = score_lead(
        purchase_timeline=lead.purchase_timeline,
        budget=lead.budget,
        vehicle_interest=lead.vehicle_interest,
        financing_need=lead.financing_need,
        trade_in_interest=lead.trade_in_interest,
        email=lead.email,
    )
    lead.score, lead.temperature, lead.conversion_probability = score, temp, prob
    db.add(lead)
    db.flush()
    log_activity(db, user_id=user.id, action="lead_created",
                 entity_type="lead", entity_id=lead.id)
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db),
             _: User = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: int,
    body: LeadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(lead, k, v)
    # Re-score on any qualification change.
    score, temp, prob = score_lead(
        purchase_timeline=lead.purchase_timeline,
        budget=lead.budget,
        vehicle_interest=lead.vehicle_interest,
        financing_need=lead.financing_need,
        trade_in_interest=lead.trade_in_interest,
        email=lead.email,
        sentiment=lead.sentiment,
    )
    lead.score, lead.temperature, lead.conversion_probability = score, temp, prob
    db.add(lead)
    log_activity(db, user_id=user.id, action="lead_updated",
                 entity_type="lead", entity_id=lead.id)
    return lead


@router.post("/{lead_id}/notes", response_model=SalesNoteOut, status_code=201)
def add_note(
    lead_id: int,
    body: SalesNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    if not db.get(Lead, lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    note = SalesNote(lead_id=lead_id, author_id=user.id,
                     category=body.category, body=body.body)
    db.add(note)
    db.flush()
    return note


@router.get("/{lead_id}/notes", response_model=list[SalesNoteOut])
def list_notes(lead_id: int, db: Session = Depends(get_db),
               _: User = Depends(get_current_user)):
    return (
        db.query(SalesNote)
        .filter(SalesNote.lead_id == lead_id)
        .order_by(SalesNote.created_at.desc())
        .all()
    )

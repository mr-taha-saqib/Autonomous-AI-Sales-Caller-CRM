"""Call management — initiate outbound calls, browse history & transcripts."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_agent
from app.core.config import settings
from app.core.database import get_db
from app.core.logging import get_logger
from app.models.call import Call, CallDirection, CallStatus
from app.models.lead import Lead
from app.models.user import User
from app.schemas.call import CallDetail, CallList, CallOut, OutboundCallRequest
from app.schemas.common import Message
from app.services import twilio_service
from app.services.audit import log_activity

log = get_logger("calls")
router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/outbound", response_model=CallOut, status_code=201)
def start_outbound_call(
    body: OutboundCallRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_agent),
):
    if body.lead_id:
        lead = db.get(Lead, body.lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

    call = Call(
        direction=CallDirection.OUTBOUND,
        status=CallStatus.QUEUED,
        from_number=settings.TWILIO_CALLER_ID,
        to_number=body.to_number,
        lead_id=body.lead_id,
    )
    db.add(call)
    db.flush()

    try:
        sid = twilio_service.place_outbound_call(body.to_number, call.id)
        call.twilio_sid = sid
        call.status = CallStatus.INITIATED
    except Exception as exc:  # noqa: BLE001
        call.status = CallStatus.FAILED
        log.error("outbound_failed", error=str(exc))
        db.add(call)
        raise HTTPException(status_code=502, detail=f"Twilio error: {exc}")

    db.add(call)
    log_activity(db, user_id=user.id, action="call_started",
                 entity_type="call", entity_id=call.id,
                 detail={"to": body.to_number})
    return call


@router.get("", response_model=CallList)
def list_calls(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    direction: CallDirection | None = None,
    status: CallStatus | None = None,
):
    q = db.query(Call)
    if direction:
        q = q.filter(Call.direction == direction)
    if status:
        q = q.filter(Call.status == status)
    total = q.count()
    items = (
        q.order_by(Call.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return CallList(total=total, page=page, page_size=page_size, items=items)


@router.get("/{call_id}", response_model=CallDetail)
def get_call(call_id: int, db: Session = Depends(get_db),
             _: User = Depends(get_current_user)):
    call = db.get(Call, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

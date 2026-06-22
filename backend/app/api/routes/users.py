"""User management (admin only)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.schemas.common import Message
from app.services.audit import log_activity

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        full_name=body.full_name,
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        role=body.role,
        phone=body.phone,
    )
    db.add(user)
    db.flush()
    log_activity(db, user_id=admin.id, action="user_created",
                 entity_type="user", entity_id=user.id)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = body.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data.pop("password"))
    else:
        data.pop("password", None)
    for k, v in data.items():
        setattr(user, k, v)
    db.add(user)
    log_activity(db, user_id=admin.id, action="user_updated",
                 entity_type="user", entity_id=user.id)
    return user


@router.delete("/{user_id}", response_model=Message)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate yourself")
    user.is_active = False
    db.add(user)
    log_activity(db, user_id=admin.id, action="user_deactivated",
                 entity_type="user", entity_id=user.id)
    return Message(detail="User deactivated")

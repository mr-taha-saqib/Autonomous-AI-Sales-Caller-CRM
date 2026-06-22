from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.AGENT
    phone: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    role: UserRole | None = None
    phone: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    phone: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}

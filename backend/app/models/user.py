"""User accounts and roles (RBAC)."""
from __future__ import annotations

import enum

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, enum_column


class UserRole(str, enum.Enum):
    ADMIN = "admin"          # full access, user management
    MANAGER = "manager"      # analytics, all leads/calls, no user mgmt
    AGENT = "agent"          # own leads/calls/appointments
    VIEWER = "viewer"        # read-only dashboards


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        enum_column(UserRole, "user_role"), default=UserRole.AGENT, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    appointments = relationship("Appointment", back_populates="sales_rep")
    sales_notes = relationship("SalesNote", back_populates="author")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role})>"

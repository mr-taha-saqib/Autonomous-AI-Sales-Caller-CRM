"""Customer master record (CRM contact)."""
from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    do_not_call: Mapped[bool] = mapped_column(default=False, nullable=False)

    leads = relationship("Lead", back_populates="customer")
    calls = relationship("Call", back_populates="customer")
    appointments = relationship("Appointment", back_populates="customer")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Customer {self.phone}>"

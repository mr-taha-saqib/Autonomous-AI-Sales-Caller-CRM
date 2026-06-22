"""SQLAlchemy engine, session factory and declarative base."""
from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
)

from app.core.config import settings

# Portable JSON column: JSONB on PostgreSQL, generic JSON elsewhere (e.g. SQLite tests).
JSONVariant = JSON().with_variant(JSONB(), "postgresql")


def enum_column(enum_cls, name: str):
    """SQLAlchemy Enum that persists member VALUES (e.g. 'admin'), not names.

    This keeps the ORM, Alembic migrations and raw SQL schema consistent — all of
    which use the lowercase enum values.
    """
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda obj: [e.value for e in obj],
        native_enum=True,
    )

def _engine_kwargs(url: str) -> dict:
    """Pool tuning for real databases; SQLite's pool rejects those kwargs."""
    if url.startswith("sqlite"):
        # SQLite (used in tests) uses SingletonThreadPool — no size/overflow.
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20}


engine = create_engine(settings.DATABASE_URL, echo=False, **_engine_kwargs(settings.DATABASE_URL))

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base with shared timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def get_db() -> Generator:
    """FastAPI dependency that yields a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

"""Pytest fixtures — in-memory SQLite app + authenticated client."""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("ANTHROPIC_API_KEY", "test")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import database
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    # Seed an admin
    db.add(User(
        full_name="Test Admin", email="admin@test.com",
        hashed_password=hash_password("Password!123"), role=UserRole.ADMIN,
    ))
    db.commit()
    yield db, TestingSession
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    _, TestingSession = db_session

    def override_get_db():
        s = TestingSession()
        try:
            yield s
            s.commit()
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "Password!123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

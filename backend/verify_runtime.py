"""Runtime verification harness (no Docker/Postgres needed).

Exercises health, JWT auth, RBAC (403), Twilio webhook route registration,
and the Claude + Twilio integration code paths with the external services mocked.
Prints a PASS/FAIL matrix and exits non-zero on any failure.
"""
import os
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["ANTHROPIC_API_KEY"] = "test"
os.environ["TWILIO_AUTH_TOKEN"] = ""
os.environ["TWILIO_ACCOUNT_SID"] = "ACtest"
os.environ["TWILIO_CALLER_ID"] = "+15551234567"

from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole

results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")


# --- in-memory DB wired into the app ---
engine = create_engine("sqlite+pysqlite:///:memory:",
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)

db = TestingSession()
db.add(User(full_name="Admin", email="admin@x.com",
            hashed_password=hash_password("Password!123"), role=UserRole.ADMIN))
db.add(User(full_name="Viewer", email="viewer@x.com",
            hashed_password=hash_password("Password!123"), role=UserRole.VIEWER))
db.commit()
db.close()


def override_db():
    s = TestingSession()
    try:
        yield s
        s.commit()
    finally:
        s.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


# 14. Health
r = client.get("/health")
check("14. /health responds 200 + ok", r.status_code == 200 and r.json()["status"] == "ok")

# 15. JWT auth
login = client.post("/api/v1/auth/login",
                    data={"username": "admin@x.com", "password": "Password!123"})
check("15a. JWT login issues tokens",
      login.status_code == 200 and "access_token" in login.json())
admin_tok = login.json()["access_token"]
me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_tok}"})
check("15b. Bearer token authenticates /me", me.status_code == 200)
check("15c. Missing token rejected (401)", client.get("/api/v1/auth/me").status_code == 401)
check("15d. Bad password rejected (401)",
      client.post("/api/v1/auth/login",
                  data={"username": "admin@x.com", "password": "wrong-pass-1"}).status_code == 401)

# 16. RBAC — viewer must NOT access admin-only user management
vlogin = client.post("/api/v1/auth/login",
                     data={"username": "viewer@x.com", "password": "Password!123"})
vtok = vlogin.json()["access_token"]
admin_list = client.get("/api/v1/users", headers={"Authorization": f"Bearer {admin_tok}"})
viewer_list = client.get("/api/v1/users", headers={"Authorization": f"Bearer {vtok}"})
check("16a. Admin can list users (200)", admin_list.status_code == 200)
check("16b. Viewer blocked from user mgmt (403)", viewer_list.status_code == 403)

# 17. Twilio webhook routes registered
paths = {getattr(r, "path", "") for r in app.routes}
for p in ["/api/v1/webhooks/twilio/voice", "/api/v1/webhooks/twilio/gather",
          "/api/v1/webhooks/twilio/status", "/api/v1/webhooks/twilio/inbound"]:
    check(f"17. webhook route {p} registered", p in paths)

# 18. Twilio outbound code path (mock the SDK call)
with patch("app.api.routes.calls.twilio_service.place_outbound_call",
           return_value="CA_mock_sid") as mock_call:
    out = client.post("/api/v1/calls/outbound",
                      json={"to_number": "+15558675309"},
                      headers={"Authorization": f"Bearer {admin_tok}"})
check("18. Outbound call path -> Twilio SDK invoked",
      out.status_code == 201 and out.json()["twilio_sid"] == "CA_mock_sid"
      and mock_call.called)

# 19. Claude integration code path (mock Anthropic client)
from app.services import claude_service
fake = MagicMock()
fake_block = MagicMock(); fake_block.type = "text"; fake_block.text = "Hi, this is Algorixe!"
fake.messages.create.return_value = MagicMock(content=[fake_block])
with patch("app.services.claude_service.get_client", return_value=fake):
    reply = claude_service.generate_reply(
        [{"role": "assistant", "content": "opening"},
         {"role": "user", "content": "hello"}])
check("19. Claude generate_reply returns text", reply == "Hi, this is Algorixe!")

# Claude tool-use extraction path
fake2 = MagicMock()
tool_block = MagicMock(); tool_block.type = "tool_use"; tool_block.name = "record_lead"
tool_block.input = {"vehicle_interest": "SUV", "budget": "$40k"}
fake2.messages.create.return_value = MagicMock(content=[tool_block])
with patch("app.services.claude_service.get_client", return_value=fake2):
    fields = claude_service.extract_lead_fields("Agent: hi\nCustomer: I want an SUV")
check("19b. Claude tool-use extraction returns CRM fields",
      fields.get("vehicle_interest") == "SUV")

print("\n=== SUMMARY ===")
passed = sum(1 for _, ok in results if ok)
print(f"{passed}/{len(results)} checks passed")
raise SystemExit(0 if passed == len(results) else 1)

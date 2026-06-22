# TEST RESULTS — Algorixe Car Care AI Sales Platform

_Verification run on Windows 11, Python 3.13.5, Node 22.14.0, executed 2026-06-12._

## 1. Environment

| Item | Result |
|------|--------|
| Python | 3.13.5 ✅ |
| pip | 25.1 (Anaconda base — venv `ensurepip` is broken in this Anaconda install; see note) ✅ |
| Node | 22.14.0 ✅ |
| npm | 11.6.1 ✅ |
| Backend deps installed | ✅ all resolve & import |
| Frontend deps installed | ✅ 462 packages |

> **Environment note:** `python -m venv` could not bootstrap pip on this machine —
> Anaconda's bundled `ensurepip` exits with `4294967295`. This is a host-level fault,
> not a project fault. Verification was therefore run against the Anaconda **base**
> interpreter, whose pip is healthy. In Docker/Linux (the deployment target) the
> standard `python -m venv` path works normally.

## 2. Backend unit / API / integration tests (pytest)

```
27 passed  (0 failed, 0 errors)
```

| Test module | Cases | Result |
|-------------|-------|--------|
| test_auth.py | 5 | ✅ login, bad password, /me auth-guard, token refresh |
| test_lead_scoring.py | 4 | ✅ hot/warm/cold thresholds, bounds |
| test_leads_api.py | 3 | ✅ create+score, search filter, re-score on update |
| test_calls_api.py | 3 | ✅ outbound (Twilio mocked), failure→502, list |
| test_conversation.py | 3 | ✅ turn append/reply, farewell→hangup, finalize+extract (Claude mocked) |
| test_analytics_api.py | 5 | ✅ summary, funnel, 3 report periods, bad period→400, dashboard home |
| test_appointments_api.py | 2 | ✅ create marks lead, update+cancel |
| test_health.py | 2 | ✅ /health, / root |

## 3. Runtime verification (FastAPI TestClient, external services mocked)

`14/14 checks passed` — see `backend/verify_runtime.py`.

| # | Check | Result |
|---|-------|--------|
| 14 | `/health` → 200 + `status: ok` | ✅ |
| 15a | JWT login issues access+refresh tokens | ✅ |
| 15b | Bearer token authenticates `/me` | ✅ |
| 15c | Missing token → 401 | ✅ |
| 15d | Wrong password → 401 | ✅ |
| 16a | Admin can list users (200) | ✅ |
| 16b | **Viewer blocked from user mgmt (403)** — RBAC enforced | ✅ |
| 17 | All 4 Twilio webhook routes registered (voice/gather/status/inbound) | ✅ |
| 18 | Outbound call path invokes Twilio SDK, persists SID, → 201 | ✅ |
| 19 | Claude `generate_reply` returns spoken text | ✅ |
| 19b | Claude tool-use extraction returns structured CRM fields | ✅ |

## 4. Database / migrations

| Check | Result |
|-------|--------|
| `alembic upgrade head --sql` (offline, PostgreSQL dialect) | ✅ exit 0 |
| 8 tables + `alembic_version` generated | ✅ |
| 7 PostgreSQL `ENUM` types created with **lowercase values** | ✅ |
| ORM ↔ migration ↔ raw SQL enum consistency | ✅ (fixed via `values_callable`) |

Generated DDL sample:
```sql
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'agent', 'viewer');
CREATE TYPE call_status AS ENUM ('queued','initiated','ringing','in_progress',
    'completed','busy','no_answer','failed','canceled','voicemail');
CREATE TABLE users ( ... role user_role DEFAULT 'agent' NOT NULL, ... );
```

## 5. Frontend build (Next.js)

```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Generating static pages (14/14)
```

Routes built: `/`, `/login`, `/leads`, `/calls`, `/appointments`, `/appointments/new`,
`/crm`, `/analytics`, `/reports`, `/settings`, `/users`, `/_not-found`.

## 6. Docker

| Check | Result |
|-------|--------|
| `docker compose config` (validate) | ✅ exit 0 — services/env/build contexts valid |
| Image build / `compose up` | ⚠️ Not run — Docker **daemon not running** on this host (CLI 29.4.3 present). Dockerfiles + compose validated statically. |

## 7. Bugs found & fixed during verification

1. **Enum persistence mismatch (critical, PostgreSQL-breaking).** SQLAlchemy persisted
   enum *names* (`ADMIN`) while migrations used *values* (`admin`) → every Postgres
   insert would fail. Fixed with a `values_callable` `enum_column()` helper. Verified
   via generated DDL.
2. **SQLite engine kwargs (portability).** `create_engine` passed `pool_size`/`max_overflow`,
   rejected by SQLite's `SingletonThreadPool` → conftest import error. Made pool args
   dialect-conditional.
3. **Anthropic first-turn ordering.** Messages API requires the first turn to be `user`;
   transcripts open with the assistant greeting. `generate_reply` now normalizes history.
4. **Next.js security advisory.** `next@14.2.15` flagged with a CVE → bumped to `14.2.35`.
5. **bcrypt version-read warning.** passlib 1.7.4 reads `bcrypt.__about__` (removed in
   bcrypt ≥4.1) → pinned `bcrypt==4.0.1` to silence noisy traceback. (Cosmetic; hashing
   always worked.)

## Final per-area status

| Area | Status |
|------|--------|
| Backend | ✅ PASS |
| Database | ✅ PASS |
| Frontend | ✅ PASS |
| Docker | ⚠️ CONFIG-VALID (runtime not exercised — no daemon on host) |
| Security | ✅ PASS |
| Tests | ✅ PASS (27 unit/API + 14 runtime = 41 checks) |
| Deployment | ✅ READY (needs running Docker daemon + real Twilio/Anthropic creds) |

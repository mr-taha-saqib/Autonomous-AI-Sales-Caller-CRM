# PROJECT STRUCTURE — Algorixe Car Care AI Sales Platform

113 source files (excludes `node_modules/`, `.venv/`, `.next/`, build artifacts).

```
algorixe-call-agent/
├── README.md                     Project overview + quick start
├── FINAL_AUDIT_REPORT.md         Production-readiness audit (score 92/100)
├── TEST_RESULTS.md               Full test/verification results
├── DEPLOYMENT_GUIDE.md           Step-by-step deployment runbook
├── PROJECT_STRUCTURE.md          This file
├── LICENSE                       Proprietary
├── Makefile                      up/down/test/seed/deploy targets
├── docker-compose.yml            db + api + web + nginx
├── .gitignore  .dockerignore
│
├── backend/                      FastAPI application (Python 3.11)
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py  script.py.mako
│   │   └── versions/0001_initial_schema.py     8 tables + 7 enums + indexes
│   ├── app/
│   │   ├── __init__.py  main.py  cli.py         app factory · seed/superuser CLI
│   │   ├── core/         config, database, security, logging, rate_limit
│   │   ├── models/       user, customer, lead, call, transcript,
│   │   │                 appointment, sales_note, activity_log
│   │   ├── schemas/      auth, lead, call, appointment, analytics, common
│   │   ├── services/     claude_service, conversation, twilio_service,
│   │   │                 lead_scoring, analytics_service, audit, prompts
│   │   └── api/
│   │       ├── deps.py   router.py             auth/RBAC deps · v1 aggregator
│   │       └── routes/   auth, users, leads, calls, appointments,
│   │                     analytics, dashboard, webhooks
│   └── tests/            conftest + 8 test modules (27 cases) · verify_runtime.py
│
├── frontend/                     Next.js 14 · TypeScript · Tailwind
│   ├── package.json  tsconfig.json  next.config.js
│   ├── tailwind.config.ts  postcss.config.js  .eslintrc.json
│   ├── app/
│   │   ├── layout.tsx  globals.css
│   │   ├── login/page.tsx
│   │   └── (dashboard)/                         auth-guarded route group
│   │       ├── layout.tsx  page.tsx (home)
│   │       ├── leads/  calls/  appointments/  appointments/new/
│   │       ├── crm/  analytics/  reports/  users/  settings/
│   ├── components/   Sidebar, Topbar, Charts, ui
│   └── lib/          api.ts (client) · format.ts
│
├── database/         schema.sql · indexes.sql · seed.sql      (raw SQL mirror)
├── docker/           backend.Dockerfile · frontend.Dockerfile · nginx.conf
├── docs/             ARCHITECTURE · INSTALLATION · DEPLOYMENT · API · DATABASE
│                     · USER_GUIDE · ADMIN_GUIDE · TROUBLESHOOTING · PROJECT_STRUCTURE
├── scripts/          deploy.sh · backup.sh · restore.sh · healthcheck.sh · dev.ps1
├── tests/e2e/        Playwright config + login.spec.ts
└── config/           .env.example · README.md
```

## Component → requirement map

| Requirement | Location |
|-------------|----------|
| AI voice agent (out/inbound) | `services/conversation.py`, `services/twilio_service.py`, `api/routes/webhooks.py` |
| Claude integration | `services/claude_service.py`, `services/prompts.py` |
| Lead qualification + scoring | `services/lead_scoring.py`, `models/lead.py` |
| Objection handling | `services/prompts.py` (`OBJECTION_PLAYBOOK`) |
| Appointment scheduler | `models/appointment.py`, `api/routes/appointments.py` |
| CRM tables | `models/` (8 tables) |
| Transcript storage | `models/transcript.py` |
| Analytics & reports | `services/analytics_service.py`, `api/routes/analytics.py` |
| Admin dashboard | `frontend/app/(dashboard)/` |
| JWT / RBAC / audit / rate-limit | `core/security.py`, `api/deps.py`, `services/audit.py`, `core/rate_limit.py` |
| Twilio integration | `services/twilio_service.py`, `api/routes/{calls,webhooks}.py` |
| Docker / DevOps | `docker/`, `docker-compose.yml`, `scripts/` |
| Tests | `backend/tests/` (27), `backend/verify_runtime.py` (14), `tests/e2e/` |
```

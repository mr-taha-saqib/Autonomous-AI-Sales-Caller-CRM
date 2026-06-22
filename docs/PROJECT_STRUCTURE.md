# Project Structure

```
algorixe-call-agent/
├── README.md
├── LICENSE
├── Makefile
├── docker-compose.yml
├── .env.example → config/.env.example
│
├── backend/                      FastAPI application
│   ├── app/
│   │   ├── main.py               app factory, middleware, health
│   │   ├── cli.py                seed / createsuperuser
│   │   ├── core/                 config, database, security, logging, rate_limit
│   │   ├── models/               SQLAlchemy ORM (8 tables)
│   │   ├── schemas/              Pydantic request/response models
│   │   ├── services/             claude, twilio, conversation, scoring, analytics, audit, prompts
│   │   └── api/
│   │       ├── deps.py           auth + RBAC dependencies
│   │       ├── router.py         API v1 aggregator
│   │       └── routes/           auth, users, leads, calls, appointments, analytics, dashboard, webhooks
│   ├── alembic/                  migrations (0001_initial_schema)
│   ├── tests/                    pytest: auth, scoring, leads, calls, conversation, analytics, appointments, health
│   └── requirements.txt
│
├── frontend/                     Next.js 14 + TS + Tailwind
│   ├── app/
│   │   ├── login/                sign-in
│   │   └── (dashboard)/          guarded console: home, leads, calls, appointments, crm, analytics, reports, users, settings
│   ├── components/               Sidebar, Topbar, Charts, ui
│   └── lib/                      api client, formatters
│
├── database/                     schema.sql, indexes.sql, seed.sql
├── docker/                       backend/frontend Dockerfiles, nginx.conf
├── scripts/                      deploy, backup, restore, healthcheck, dev.ps1
├── tests/                        e2e (Playwright)
├── config/                       .env.example
└── docs/                         install, deploy, api, database, architecture, user, admin, troubleshooting
```

## Component → requirement mapping

| Requirement            | Where |
|------------------------|-------|
| AI voice agent         | `services/conversation.py`, `services/twilio_service.py`, `api/routes/webhooks.py` |
| Claude integration     | `services/claude_service.py`, `services/prompts.py` |
| Lead qualification+scoring | `services/lead_scoring.py`, `models/lead.py` |
| Objection handling     | `services/prompts.py` (`OBJECTION_PLAYBOOK`) |
| Appointment scheduler  | `models/appointment.py`, `api/routes/appointments.py` |
| CRM tables             | `models/` (customers, leads, calls, appointments, sales_notes, users, activity_logs) |
| Transcript storage     | `models/transcript.py` |
| Analytics & reports    | `services/analytics_service.py`, `api/routes/analytics.py` |
| Admin dashboard        | `frontend/app/(dashboard)/` |
| Security (JWT/RBAC/audit) | `core/security.py`, `api/deps.py`, `services/audit.py`, `core/rate_limit.py` |
| Twilio integration     | `services/twilio_service.py`, `api/routes/webhooks.py`, `api/routes/calls.py` |
```

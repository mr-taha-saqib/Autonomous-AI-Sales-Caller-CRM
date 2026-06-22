# Algorixe Car Care — AI Cold-Calling & Sales Platform

A production-grade, AI-powered outbound/inbound cold-calling platform for **Algorixe Car Care**.
The **Algorixe Sales Assistant** makes natural phone calls (Twilio Voice), qualifies leads,
handles objections, books appointments, and writes everything back to a built-in CRM — powered
by the **Claude API**.

```
┌──────────────┐     Twilio Voice     ┌───────────────┐     Claude API
│   Prospect   │ ◄──────────────────► │   FastAPI     │ ◄────────────────► Anthropic
│   (phone)    │   PSTN / WebRTC      │   Backend     │   conversation LLM
└──────────────┘                      └──────┬────────┘
                                             │ SQLAlchemy
                                       ┌──────▼────────┐       ┌──────────────┐
                                       │  PostgreSQL   │ ◄──── │  Next.js     │
                                       │  CRM + logs   │  REST │  Dashboard   │
                                       └───────────────┘       └──────────────┘
```

## Tech Stack

| Layer            | Technology                                  |
|------------------|---------------------------------------------|
| Backend          | Python 3.11, FastAPI, SQLAlchemy 2.x, Alembic |
| Database         | PostgreSQL 16                               |
| Frontend         | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Auth             | JWT (access + refresh), bcrypt, RBAC        |
| Voice            | Twilio Voice (outbound/inbound, recording, media streams) |
| AI Engine        | Claude API (`claude-opus-4-8` / `claude-sonnet-4-6`) |
| Speech           | Twilio `<Gather>` STT + Amazon Polly Neural TTS |
| Deploy           | Docker, Docker Compose, Nginx              |
| Tests            | pytest, httpx, Playwright                   |

## Repository Layout

```
.
├── backend/        FastAPI application, services, models, API routers
├── frontend/       Next.js + TypeScript + Tailwind admin dashboard
├── database/       SQL schema, migrations, seed data, indexes
├── docker/         Dockerfiles + nginx config
├── docs/           Install / deploy / API / DB / architecture / user guides
├── scripts/        Deploy, backup, healthcheck, seed helpers
├── tests/          Unit, API, integration, e2e tests
├── config/         Environment templates and shared config
└── docker-compose.yml
```

## Quick Start (Local, Docker)

```bash
git clone <repo> algorixe-call-agent && cd algorixe-call-agent
cp config/.env.example .env          # fill in TWILIO_* and ANTHROPIC_API_KEY
docker compose up --build            # api:8000, web:3000, db:5432
docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli seed
```

Open the dashboard at **http://localhost:3000** and log in with the seeded admin:

```
email:    admin@algorixe.com
password: ChangeMe!123
```

API docs (OpenAPI/Swagger): **http://localhost:8000/docs**

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/API.md)
- [Database Documentation](docs/DATABASE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Admin Guide](docs/ADMIN_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## License

Proprietary — © Algorixe Car Care. All rights reserved.

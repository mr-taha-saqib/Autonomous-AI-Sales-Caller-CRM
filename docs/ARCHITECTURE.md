# Architecture

## High-level

```
                         ┌──────────────────────────────────────────────┐
                         │                Algorixe Platform              │
                         │                                                │
  Prospect phone  ◄────► │  Twilio Voice ◄──► FastAPI ◄──► Claude API     │
  (PSTN)                 │       │             │   │                      │
                         │  (TwiML / Gather)   │   └── lead scoring        │
                         │                     │                          │
  Sales team browser ◄─► │  Next.js dashboard ─┴── PostgreSQL (CRM)        │
                         └──────────────────────────────────────────────┘
```

## Components

### 1. FastAPI backend (`backend/`)
- **API layer** (`app/api/routes`): REST endpoints for auth, leads, calls,
  appointments, analytics, users, dashboard, and Twilio webhooks.
- **Services** (`app/services`): the business logic —
  - `claude_service` — Claude Messages API for live turns, extraction, summary.
  - `conversation` — orchestrates Twilio ↔ Claude ↔ CRM, owns transcript state.
  - `twilio_service` — places calls, builds TwiML (`<Gather>`/`<Say>`).
  - `lead_scoring` — deterministic, explainable hot/warm/cold scoring.
  - `analytics_service` — aggregations & reports.
- **Models** (`app/models`): SQLAlchemy 2.0 ORM — users, customers, leads,
  calls, transcripts, appointments, sales_notes, activity_logs.
- **Core** (`app/core`): config, DB engine, JWT security, logging, rate limiting.

### 2. The call loop
1. Agent (or campaign) triggers `POST /api/v1/calls/outbound`.
2. `twilio_service.place_outbound_call` dials and points Twilio at
   `/webhooks/twilio/voice`.
3. On answer, the backend speaks an opening line and `<Gather>`s speech.
4. Each customer utterance hits `/webhooks/twilio/gather`; `conversation.next_turn`
   appends it to the transcript, asks Claude for the next reply, and returns TwiML.
5. On `completed` status, `conversation.finalize_call` runs Claude summarisation
   and CRM extraction, then re-scores the lead.

```
Twilio ──POST /voice──►  speak opening, Gather
   ▲                          │
   │  TwiML (Say + Gather)     ▼
   └──POST /gather──◄── Claude.generate_reply(history)
                              │
        on hangup ──► /status ──► Claude.summarise + extract ──► Lead scoring
```

### 3. Next.js dashboard (`frontend/`)
App Router + TypeScript + Tailwind. JWT stored client-side; an auth-guarded
`(dashboard)` route group renders the console (Dashboard, Leads, Calls,
Appointments, CRM, Analytics, Reports, Users, Settings). Recharts for charts,
dark mode via the Tailwind `class` strategy.

### 4. PostgreSQL
Normalised CRM schema with JSONB transcript storage and GIN/trigram indexes for
search. Migrations via Alembic; a parallel raw-SQL schema lives in `database/`.

## Data model (entities & relationships)

```
users ──< appointments >── leads ──< calls ──1:1── transcripts
                              │         │
              sales_notes >───┘         └──> customers
activity_logs (audit, references users)
```

- `customers` 1─* `leads` 1─* `calls` 1─1 `transcripts`
- `leads` 1─* `appointments` *─1 `users` (sales rep)
- `leads` 1─* `sales_notes` *─1 `users` (author)
- `activity_logs` *─1 `users`

## Security model
- JWT access (30 min) + refresh (7 day) tokens, HS256.
- bcrypt password hashing (configurable rounds).
- RBAC: `admin` > `manager` > `agent` > `viewer` enforced via FastAPI deps.
- Twilio webhook signature validation.
- Rate limiting (slowapi), CORS allow-list, parameterised queries (no raw SQL),
  Pydantic input validation, and an immutable `activity_logs` audit trail.

## Scaling notes
- Backend is stateless (conversation state lives in Postgres) → scale `api`
  horizontally behind nginx.
- Swap slowapi's in-memory store for Redis in multi-instance deployments.
- Move call summarisation/extraction to a background worker (e.g. RQ/Celery)
  for very high call volumes.

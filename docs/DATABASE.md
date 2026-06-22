# Database Documentation

PostgreSQL 16. Canonical schema = Alembic migrations (`backend/alembic`); a
mirror lives in `database/schema.sql` + `database/indexes.sql`.

## Tables

### users
Auth + RBAC. `role ∈ {admin, manager, agent, viewer}`. `email` unique.

### customers
Master contact, deduped by `phone` (unique). `do_not_call` flag honoured by the agent.

### leads
Qualification record + scoring.
- Capture: `full_name, email, location, budget, vehicle_interest,
  purchase_timeline, financing_need, trade_in_interest`.
- Scoring: `score (0-100)`, `temperature {hot,warm,cold}`,
  `conversion_probability`.
- Pipeline: `status {new, contacted, qualified, appointment_set, converted,
  lost, do_not_call}`.
- AI: `intent_summary`, `sentiment`.

### calls
One row per Twilio call. `direction`, `status`, `from/to_number`,
`duration_seconds`, `recording_url`, plus AI-derived `summary, key_intent,
sentiment, outcome`. FK → `leads`, `customers`.

### transcripts
1:1 with `calls`. `turns` JSONB array of `{role, text, ts}`, `full_text`, and
AI `summary/key_intent/sentiment/outcome`. GIN index on `turns`.

### appointments
`appointment_type {showroom_visit, virtual_consultation}`,
`status {scheduled, confirmed, completed, canceled, no_show, rescheduled}`,
`scheduled_for`, `location`/`meeting_link`. FK → leads, customers, users(rep).

### sales_notes
Free-form notes per lead, authored by a user.

### activity_logs
Immutable audit trail: `user_id, action, entity_type, entity_id, ip_address,
detail (JSONB)`.

## Relationships
```
customers 1─* leads 1─* calls 1─1 transcripts
leads 1─* appointments *─1 users
leads 1─* sales_notes *─1 users
users 1─* activity_logs
```

## Indexes (see `database/indexes.sql`)
- B-tree: emails, phones, statuses, temperatures, `scheduled_for`, `created_at`.
- `leads.score DESC` for hot-lead ranking.
- Trigram (`pg_trgm`) GIN on `leads.full_name` for fuzzy search.
- JSONB GIN on `transcripts.turns`.

## Migrations
```bash
cd backend
alembic upgrade head                      # apply
alembic revision --autogenerate -m "msg"  # create new
alembic downgrade -1                       # roll back one
```

## Example optimised queries
```sql
-- Hottest open leads
SELECT id, full_name, phone, score
FROM leads
WHERE status IN ('new','contacted','qualified')
ORDER BY score DESC
LIMIT 20;

-- Appointment conversion this month
SELECT count(*) FILTER (WHERE status='completed')::float
       / NULLIF(count(*),0) AS conversion
FROM appointments
WHERE scheduled_for >= date_trunc('month', now());
```

# API Documentation

Base URL: `http://localhost:8000`  ·  Interactive docs: `/docs` (Swagger), `/redoc`.
All `/api/v1/*` endpoints (except auth and Twilio webhooks) require
`Authorization: Bearer <access_token>`.

## Auth

| Method | Path                    | Body                                   | Notes |
|--------|-------------------------|----------------------------------------|-------|
| POST   | `/api/v1/auth/login`    | form: `username` (email), `password`   | → `{access_token, refresh_token}` |
| POST   | `/api/v1/auth/refresh`  | `{refresh_token}`                       | new token pair |
| GET    | `/api/v1/auth/me`       | —                                       | current user |

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@algorixe.com&password=ChangeMe!123"
```

## Leads

| Method | Path                          | Roles | Description |
|--------|-------------------------------|-------|-------------|
| GET    | `/api/v1/leads`               | any   | list; filters: `temperature`, `status`, `search`, `page`, `page_size` |
| POST   | `/api/v1/leads`               | agent+| create (auto-scored) |
| GET    | `/api/v1/leads/{id}`          | any   | detail |
| PATCH  | `/api/v1/leads/{id}`          | agent+| update + re-score |
| POST   | `/api/v1/leads/{id}/notes`    | agent+| add sales note |
| GET    | `/api/v1/leads/{id}/notes`    | any   | list notes |

## Calls

| Method | Path                          | Roles | Description |
|--------|-------------------------------|-------|-------------|
| POST   | `/api/v1/calls/outbound`      | agent+| `{to_number, lead_id?}` → starts AI call |
| GET    | `/api/v1/calls`               | any   | history; filters: `direction`, `status` |
| GET    | `/api/v1/calls/{id}`          | any   | detail incl. transcript |

## Appointments

| Method | Path                          | Roles | Description |
|--------|-------------------------------|-------|-------------|
| GET    | `/api/v1/appointments`        | any   | filters: `status`, `sales_rep_id`, `upcoming` |
| POST   | `/api/v1/appointments`        | agent+| create (`showroom_visit`/`virtual_consultation`) |
| PATCH  | `/api/v1/appointments/{id}`   | agent+| update/reschedule/status |
| DELETE | `/api/v1/appointments/{id}`   | agent+| cancel |

## Analytics

| Method | Path                              | Roles    | Description |
|--------|-----------------------------------|----------|-------------|
| GET    | `/api/v1/analytics/summary`       | any      | KPI summary |
| GET    | `/api/v1/analytics/funnel`        | any      | funnel stages |
| GET    | `/api/v1/analytics/reports/{period}` | manager+ | `daily`/`weekly`/`monthly` |
| GET    | `/api/v1/dashboard/home`          | any      | home aggregate feed |

## Users (admin)

| Method | Path                    | Description |
|--------|-------------------------|-------------|
| GET    | `/api/v1/users`         | list |
| POST   | `/api/v1/users`         | create |
| PATCH  | `/api/v1/users/{id}`    | update (role, password, active) |
| DELETE | `/api/v1/users/{id}`    | deactivate |

## Twilio webhooks (called by Twilio, signature-validated)

| Path                                  | Purpose |
|---------------------------------------|---------|
| `/api/v1/webhooks/twilio/voice`       | outbound call entry, opening line |
| `/api/v1/webhooks/twilio/gather`      | per-utterance AI turn |
| `/api/v1/webhooks/twilio/status`      | lifecycle events, finalisation |
| `/api/v1/webhooks/twilio/recording`   | recording URL callback |
| `/api/v1/webhooks/twilio/inbound`     | inbound call entry |

## Errors
Standard HTTP codes. Body shape: `{"detail": "<message>"}`.
`401` invalid/expired token · `403` insufficient role · `404` not found ·
`409` conflict · `429` rate limited · `502` upstream (Twilio) failure.

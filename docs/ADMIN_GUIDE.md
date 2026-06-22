# Admin Guide

## Roles (RBAC)
| Role     | Capabilities |
|----------|--------------|
| admin    | Everything, incl. user management |
| manager  | All leads/calls/appointments + reports; no user management |
| agent    | Create/update leads, place calls, manage appointments |
| viewer   | Read-only dashboards |

`admin` implicitly satisfies every guard.

## Managing users
**User Management** page (admin only): create users with a role, deactivate
users, or change roles/passwords via `PATCH /api/v1/users/{id}`. You cannot
deactivate your own account.

CLI alternative:
```bash
docker compose exec api python -m app.cli createsuperuser
```

## First-run hardening
1. Sign in as `admin@algorixe.com` / `ChangeMe!123`.
2. Create your real admin, then deactivate the seed admin.
3. Rotate `SECRET_KEY` and DB credentials; set `ENVIRONMENT=production`.

## Configuration (`.env`)
| Key | Purpose |
|-----|---------|
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS` | token lifetimes |
| `RATE_LIMIT_PER_MINUTE` | per-IP API rate limit |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Twilio credentials |
| `TWILIO_CALLER_ID` | outbound caller number (E.164) |
| `TWILIO_VOICE` | TTS voice (e.g. `Polly.Joanna-Neural`) |
| `ANTHROPIC_API_KEY` | Claude API key |
| `CLAUDE_MODEL` / `CLAUDE_FAST_MODEL` | conversation / extraction models |
| `PUBLIC_BASE_URL` | HTTPS URL Twilio calls back |

## Tuning the AI agent
The persona, objection playbook and extraction prompts live in
`backend/app/services/prompts.py`. Edit `SYSTEM_PROMPT` to adjust tone/goals and
`OBJECTION_PLAYBOOK` for objection responses — no call-flow changes required.

Lead scoring weights live in `backend/app/services/lead_scoring.py` and are fully
explainable; adjust thresholds (hot ≥ 65, warm ≥ 35) there.

## Twilio setup
1. Buy a voice-capable number.
2. Set the number's inbound webhook to
   `https://<host>/api/v1/webhooks/twilio/inbound` (POST).
3. Ensure `PUBLIC_BASE_URL` is HTTPS and reachable; signatures are validated.

## Audit & compliance
Every mutating action is recorded in `activity_logs`. Honour DNC: leads marked
`do_not_call` and customers with `do_not_call=true` should be excluded from
campaigns. Review local outbound-calling regulations (TCPA, etc.).

## Backups
`scripts/backup.sh` (daily cron recommended) and `scripts/restore.sh`.

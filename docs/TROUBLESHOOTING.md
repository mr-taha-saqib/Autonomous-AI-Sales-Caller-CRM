# Troubleshooting

## Backend won't start
- **`could not connect to database`** — ensure `db` is healthy
  (`docker compose ps`), and `DATABASE_URL` host matches the service name (`db`).
- **`relation "users" does not exist`** — run `alembic upgrade head`.
- **Pydantic settings error** — a required `.env` var is missing/misformatted.

## Login fails
- `401 Incorrect email or password` — verify the seed ran
  (`docker compose exec api python -m app.cli seed`).
- Token immediately rejected — `SECRET_KEY` changed after issuing tokens; log in again.

## Calls don't connect
- **Twilio error 21205/21210** — `TWILIO_CALLER_ID` not a verified/owned number.
- **Webhook never fires** — `PUBLIC_BASE_URL` not publicly reachable over HTTPS.
  Use ngrok in dev and confirm the number's webhook points to `/webhooks/twilio/inbound`.
- **`403` on webhooks** — signature validation failed; ensure `PUBLIC_BASE_URL`
  exactly matches the URL Twilio calls (scheme + host), or clear `TWILIO_AUTH_TOKEN`
  in local testing to skip validation.

## AI replies are empty or error
- `ANTHROPIC_API_KEY` missing/invalid → check logs for 401 from Anthropic.
- Rate/quota limits → the service retries with backoff; check Anthropic dashboard.
- Wrong model id → verify `CLAUDE_MODEL` (e.g. `claude-opus-4-8`).

## Speech recognition poor
- Tune `<Gather>` `speech_timeout`/`timeout` in `twilio_service.gather_speech`.
- Ensure `speech_model="phone_call"` and correct `language`.

## Frontend issues
- **Blank page / redirected to /login** — no/expired token; sign in again.
- **CORS errors** — set `FRONTEND_ORIGIN` to the dashboard's exact origin.
- **API calls 404** — check `NEXT_PUBLIC_API_BASE_URL`.

## Tests failing
- Run from `backend/` so `app` is importable.
- Tests use in-memory SQLite and mock Twilio/Claude — no external creds needed.

## Rate limited (429)
Raise `RATE_LIMIT_PER_MINUTE`, or move slowapi to a Redis backend for multi-instance.

## Health check
```bash
curl http://localhost:8000/health
# {"status":"ok","database":"ok",...}
```

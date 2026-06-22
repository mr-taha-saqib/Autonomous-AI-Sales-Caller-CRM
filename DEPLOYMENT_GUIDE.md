# DEPLOYMENT GUIDE — Algorixe Car Care AI Sales Platform

This is the authoritative, step-by-step deployment runbook. For background see
`docs/DEPLOYMENT.md` and `docs/ARCHITECTURE.md`.

---

## 0. Prerequisites

- A host with **Docker + Docker Compose v2** and a **running Docker daemon**
  (start Docker Desktop on Windows/Mac, or `systemctl start docker` on Linux).
- A **Twilio** account with a voice-capable phone number (E.164).
- An **Anthropic API key**.
- A **public HTTPS URL** that Twilio can reach (your domain, or `ngrok` for testing).

> If `docker info` errors with "cannot connect to the Docker daemon", the daemon
> is not running — start it before continuing.

---

## 1. Configure environment

```bash
cd "algorixe-call-agent"
cp config/.env.example .env
```

Edit `.env` and set at minimum:

```ini
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<openssl rand -hex 32>
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql+psycopg://algorixe:<strong-password>@db:5432/algorixe
PUBLIC_BASE_URL=https://your-domain.com        # Twilio must reach this over HTTPS
FRONTEND_ORIGIN=https://your-domain.com
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com
TWILIO_ACCOUNT_SID=ACxxxx…
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_CALLER_ID=+15551234567
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-opus-4-8
CLAUDE_FAST_MODEL=claude-sonnet-4-6
```

---

## 2. Build & start the stack

```bash
docker compose up --build -d
```

This starts four services:
- `db` — PostgreSQL 16 (healthchecked)
- `api` — FastAPI; on boot it runs `alembic upgrade head` then `python -m app.cli seed`
- `web` — Next.js dashboard
- `nginx` — reverse proxy on port 80 (routes `/api`,`/docs`,`/health` → api; `/` → web)

Verify:
```bash
docker compose ps
curl http://localhost:8000/health      # {"status":"ok","database":"ok",...}
```

Endpoints:
- Dashboard: `http://localhost:3000` (or `http://localhost` via nginx)
- API docs:  `http://localhost:8000/docs`

---

## 3. First-run hardening (do immediately)

1. Log in as the seeded admin: `admin@algorixe.com` / `ChangeMe!123`.
2. Create your real admin user, then deactivate the seeded one (Users page).
3. Confirm `ENVIRONMENT=production` and a unique `SECRET_KEY`.

```bash
# create an admin from the CLI instead, if preferred:
docker compose exec api python -m app.cli createsuperuser
```

---

## 4. Wire up Twilio

In the Twilio Console → your number → **Voice Configuration**:

- **A call comes in** → Webhook → `https://your-domain.com/api/v1/webhooks/twilio/inbound`
  (HTTP **POST**)

Outbound calls are initiated by the app (`POST /api/v1/calls/outbound`) and Twilio calls
back to `/webhooks/twilio/voice`, `/gather`, `/status`, `/recording` automatically using
`PUBLIC_BASE_URL`. Signatures are validated against `TWILIO_AUTH_TOKEN`.

For local testing:
```bash
ngrok http 8000
# set PUBLIC_BASE_URL=https://<id>.ngrok-free.app in .env, then: docker compose up -d api
```

---

## 5. TLS / HTTPS

Twilio **requires HTTPS** webhooks. Terminate TLS at nginx or an upstream load balancer:
- Easiest: put the stack behind a managed LB / Cloudflare, or
- Extend `docker/nginx.conf` with a `443` server block + mounted certs (Let's Encrypt).

---

## 6. Backups

```bash
bash scripts/backup.sh                         # → backups/algorixe-*.sql.gz (keeps 14)
# cron (daily 02:00):
0 2 * * * cd /opt/algorixe && bash scripts/backup.sh >> /var/log/algorixe-backup.log 2>&1
# restore:
bash scripts/restore.sh backups/<file>.sql.gz
```

---

## 7. Updates (zero-downtime-ish)

```bash
git pull
docker compose build api web
docker compose up -d --no-deps api web
docker compose exec -T api alembic upgrade head
```

---

## 8. Scaling & ops

- Scale API: `docker compose up -d --scale api=3` (nginx upstream balances).
- Replace slowapi in-memory limiter with Redis for correct multi-instance rate limits.
- Logs are structured JSON in production (structlog) — ship to your log stack.
- Health: container `HEALTHCHECK` on api; external probe `bash scripts/healthcheck.sh https://your-domain.com`.

---

## 9. Manual (non-Docker) deployment

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://algorixe:pass@localhost:5432/algorixe
alembic upgrade head && python -m app.cli seed
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000   # Linux
# Windows dev: uvicorn app.main:app --port 8000
```

### Frontend
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com npm run build
npm start    # serves on :3000
```

---

## 10. Post-deploy smoke test

```bash
curl https://your-domain.com/health
# login
curl -X POST https://your-domain.com/api/v1/auth/login \
  -d "username=admin@algorixe.com&password=<your-pass>"
# place a test call (use a number you own / consent to)
curl -X POST https://your-domain.com/api/v1/calls/outbound \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"to_number":"+15558675309"}'
```

If all three succeed, the platform is live.

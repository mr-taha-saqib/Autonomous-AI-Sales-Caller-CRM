# Installation Guide

## Prerequisites
- Docker + Docker Compose (recommended path), **or**
- Python 3.11+, Node.js 20+, PostgreSQL 16 (manual path)
- A Twilio account with a voice-capable phone number
- An Anthropic API key

## Option A — Docker (recommended)

```bash
git clone <repo> "algorixe-call-agent"
cd algorixe-call-agent
cp config/.env.example .env
# edit .env: SECRET_KEY, TWILIO_*, ANTHROPIC_API_KEY, PUBLIC_BASE_URL
docker compose up --build -d
```

The `api` container automatically runs `alembic upgrade head` and seeds demo data.

- Dashboard: http://localhost:3000
- API docs:  http://localhost:8000/docs
- Via nginx: http://localhost

Login: `admin@algorixe.com` / `ChangeMe!123` (change immediately).

## Option B — Manual

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://algorixe:algorixe_secret@localhost:5432/algorixe
alembic upgrade head
python -m app.cli seed
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## Exposing webhooks to Twilio (local dev)
Twilio must reach your backend over HTTPS. Use a tunnel:

```bash
ngrok http 8000
# set PUBLIC_BASE_URL=https://<your-id>.ngrok-free.app in .env, restart api
```

In the Twilio console, point your number's **A Call Comes In** webhook to:
```
https://<public-host>/api/v1/webhooks/twilio/inbound   (HTTP POST)
```

## Verify
```bash
curl http://localhost:8000/health
cd backend && pytest
```

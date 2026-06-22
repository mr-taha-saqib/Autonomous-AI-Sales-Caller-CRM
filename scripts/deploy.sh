#!/usr/bin/env bash
# Production deploy helper for Algorixe Car Care.
set -euo pipefail

echo "▶ Algorixe deploy starting…"

if [[ ! -f .env ]]; then
  echo "✖ .env missing. Copy config/.env.example to .env and fill it in." >&2
  exit 1
fi

echo "▶ Pulling latest images / rebuilding…"
docker compose pull || true
docker compose build

echo "▶ Bringing the stack up…"
docker compose up -d

echo "▶ Waiting for the database…"
until docker compose exec -T db pg_isready -U "${POSTGRES_USER:-algorixe}" >/dev/null 2>&1; do
  sleep 2
done

echo "▶ Running migrations…"
docker compose exec -T api alembic upgrade head

echo "▶ Seeding (idempotent)…"
docker compose exec -T api python -m app.cli seed || true

echo "✅ Deploy complete."
echo "   Dashboard : http://localhost:3000"
echo "   API docs  : http://localhost:8000/docs"
echo "   Via nginx : http://localhost"

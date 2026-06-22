#!/usr/bin/env bash
# Database backup → ./backups/algorixe-YYYYmmdd-HHMMSS.sql.gz
set -euo pipefail

mkdir -p backups
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="backups/algorixe-${STAMP}.sql.gz"

echo "▶ Dumping database to ${OUT}…"
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-algorixe}" \
  "${POSTGRES_DB:-algorixe}" | gzip > "${OUT}"

echo "✅ Backup written: ${OUT}"

# Retain the 14 most recent backups.
ls -1t backups/algorixe-*.sql.gz | tail -n +15 | xargs -r rm --
echo "▶ Old backups pruned (kept 14 most recent)."

#!/usr/bin/env bash
# Restore a gzipped pg_dump backup. Usage: scripts/restore.sh backups/file.sql.gz
set -euo pipefail

FILE="${1:?Usage: restore.sh <backup.sql.gz>}"
echo "⚠ This will overwrite the current database. Ctrl-C to abort."
sleep 4

gunzip -c "${FILE}" | docker compose exec -T db \
  psql -U "${POSTGRES_USER:-algorixe}" "${POSTGRES_DB:-algorixe}"

echo "✅ Restore complete from ${FILE}."

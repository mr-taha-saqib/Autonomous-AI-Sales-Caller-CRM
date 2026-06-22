#!/usr/bin/env bash
# Simple uptime probe for monitoring/cron.
set -euo pipefail

API="${1:-http://localhost:8000}"
STATUS="$(curl -fsS "${API}/health" | grep -o '"status":"[^"]*"' || echo 'unreachable')"

if echo "${STATUS}" | grep -q '"status":"ok"'; then
  echo "✅ API healthy: ${STATUS}"
  exit 0
else
  echo "✖ API unhealthy: ${STATUS}" >&2
  exit 1
fi

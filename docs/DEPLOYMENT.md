# Deployment Guide

## Production checklist
- [ ] `ENVIRONMENT=production`, `DEBUG=false`
- [ ] Strong `SECRET_KEY` (`openssl rand -hex 32`)
- [ ] Rotated `POSTGRES_PASSWORD`, restricted DB network access
- [ ] `PUBLIC_BASE_URL` set to your HTTPS domain (Twilio reachable)
- [ ] TLS termination at nginx / load balancer (Let's Encrypt)
- [ ] Default admin password changed; demo seed disabled or cleaned
- [ ] Backups scheduled (`scripts/backup.sh` via cron)
- [ ] Monitoring/alerting on `/health`

## Deploy with Compose

```bash
cp config/.env.example .env   # fill production values
bash scripts/deploy.sh
```

`deploy.sh` builds images, starts the stack, waits for Postgres, runs migrations
and idempotent seed.

## TLS
Place a TLS-terminating proxy in front of nginx (or extend `docker/nginx.conf`
with a `443` server block and mounted certs). Twilio requires HTTPS webhooks.

## Zero-downtime updates
```bash
git pull
docker compose build api web
docker compose up -d --no-deps api web
docker compose exec -T api alembic upgrade head
```

## Backups & restore
```bash
bash scripts/backup.sh                       # → backups/algorixe-*.sql.gz (keeps 14)
bash scripts/restore.sh backups/<file>.sql.gz
```
Schedule daily via cron:
```
0 2 * * * cd /opt/algorixe && bash scripts/backup.sh >> /var/log/algorixe-backup.log 2>&1
```

## Scaling
- Scale the API: `docker compose up -d --scale api=3` (nginx upstream balances).
- Replace slowapi in-memory limiter with Redis for multi-instance correctness.
- Offload call finalisation to a worker queue at high volume.

## Observability
- Structured JSON logs (structlog) in production — ship to your log stack.
- Container `HEALTHCHECK` on the API; `scripts/healthcheck.sh` for external probes.

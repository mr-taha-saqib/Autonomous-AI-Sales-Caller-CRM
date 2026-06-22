# config/

Shared configuration and environment templates.

- **`.env.example`** — copy to the project root as `.env` and fill in secrets
  (`SECRET_KEY`, `TWILIO_*`, `ANTHROPIC_API_KEY`, `PUBLIC_BASE_URL`, DB creds).

The backend reads configuration from environment variables via
`backend/app/core/config.py` (Pydantic Settings). Docker Compose passes the root
`.env` to the `api` service via `env_file`. Never commit a filled-in `.env`.

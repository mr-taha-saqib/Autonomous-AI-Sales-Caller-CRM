# Tests

| Suite                | Location                | Runner       |
|----------------------|-------------------------|--------------|
| Unit + API + integration | `backend/tests/`    | `pytest`     |
| End-to-end (browser) | `tests/e2e/`            | Playwright   |

## Backend

```bash
cd backend
pip install -r requirements.txt pytest httpx
pytest                      # runs against in-memory SQLite, mocks Twilio + Claude
```

Coverage spans authentication & JWT, RBAC, lead scoring, lead/call/appointment
APIs, the Claude-driven conversation engine (mocked), analytics, and health.

## End-to-end

Requires the full stack running (`docker compose up`).

```bash
cd tests/e2e
npm install
npm run install-browsers
E2E_BASE_URL=http://localhost:3000 npm test
```

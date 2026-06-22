# Workflows at a glance

| Workflow | Trigger | What it does | Maps to (original) |
|----------|---------|--------------|--------------------|
| **outbound-initiate** | Webhook `POST /initiate-call` or Manual/Cron | Insert `calls` row → call Twilio API → save SID | `POST /api/v1/calls/outbound` |
| **voice-conversation** | Twilio Webhook `POST /voice` and `POST /gather` | Speak opening, then per-utterance: load transcript → Claude → reply → return Gather TwiML | `/webhooks/twilio/voice` + `/gather` |
| **call-status-finalize** | Twilio Webhook `POST /status` | On `completed`: summarize + extract CRM fields (Claude tools) → score lead → update Postgres | `/webhooks/twilio/status` + `finalize_call` |
| **inbound-call** *(optional)* | Twilio "A call comes in" → `POST /inbound` | Create inbound `calls` row, greet, hand off to `/gather` loop | `/webhooks/twilio/inbound` |
| **appointments** *(optional)* | n8n Form / Webhook | Insert `appointments`, flip lead to `appointment_set`, (opt.) Google Calendar + email/SMS confirm | `/api/v1/appointments` |
| **daily-report** *(optional)* | Cron | Aggregate Postgres metrics → email summary | `/api/v1/analytics/reports/*` |

**Shared credentials:** Postgres, Twilio (Basic Auth), Anthropic (header auth).
**Public HTTPS base URL** required so Twilio can reach the webhooks.

Import the JSONs in `workflows/`, then follow `N8N_BUILD_SPEC.md` to bind credentials and the
public URL placeholders (`<n8n>`, `{{SID}}`, `{{CALLER_ID}}`).

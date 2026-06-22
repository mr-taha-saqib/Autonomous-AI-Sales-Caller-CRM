# Algorixe AI Caller — n8n Edition (Project Handoff)

This package is a **build spec for re-creating the Algorixe Car Care AI cold-calling
platform using n8n** instead of a hand-written FastAPI backend. It reuses the proven
data model, AI persona, and Twilio call flow from the original project — only the
**orchestration layer** changes from Python code to n8n workflows.

> Original (code) build: FastAPI + PostgreSQL + Next.js, fully tested & Docker-deployed.
> This handoff keeps the **same PostgreSQL schema, same Claude prompts, same Twilio
> `<Gather>`/`<Say>` call loop** — n8n becomes the glue that the FastAPI routes used to be.

## What's in this folder

| File | Purpose |
|------|---------|
| `README.md` | This overview + how to use the package |
| `N8N_BUILD_SPEC.md` | **The main doc** — every feature mapped to an n8n workflow + node-by-node design |
| `WORKFLOWS.md` | One-page summary of each workflow and its trigger |
| `prompts.md` | Claude system prompt, persona & objection playbook (reuse verbatim) |
| `schema.sql` | PostgreSQL schema to import (same as original) |
| `CREDENTIALS.example.env` | All API keys / connection settings n8n needs |
| `workflows/outbound-initiate.json` | Importable: place an outbound call |
| `workflows/voice-conversation.json` | Importable: the live AI conversation loop (Twilio ↔ Claude) |
| `workflows/call-status-finalize.json` | Importable: on hangup → summarize, extract, score lead |

## Architecture in one picture

```
                         ┌──────────────── n8n ────────────────┐
 Prospect (phone) ◄────► │  Webhook /voice  ─► Postgres (get)   │
        ▲   Twilio Voice │        │           HTTP ─► Claude     │ ◄─► Anthropic
        │                │  Respond TwiML ◄── append turn (PG)   │
        └────────────────│  Webhook /gather (loop per utterance) │ ◄─► PostgreSQL
                         │  Webhook /status ─► summarize+score    │
                         └──────────────────────────────────────┘
                                        ▲ REST/UI
                              (optional) n8n forms OR keep the Next.js dashboard
```

## How to use this handoff

1. Spin up **n8n** (self-hosted Docker or n8n Cloud) and a **PostgreSQL** instance.
2. Import `schema.sql` into Postgres.
3. In n8n, create credentials for **Postgres**, **Twilio**, and **Anthropic** (see `CREDENTIALS.example.env`).
4. Import the three workflow JSONs from `workflows/` and bind them to your credentials.
5. Expose n8n over HTTPS (n8n Cloud gives you this; self-host needs a public URL/reverse proxy) and point your **Twilio number's voice webhook** at the `voice-conversation` webhook URL.
6. Paste the contents of `prompts.md` into the Claude HTTP node's `system` field.
7. Follow `N8N_BUILD_SPEC.md` node-by-node to wire and test.

## Why this maps cleanly

Every FastAPI route in the original has a 1:1 n8n equivalent:

| Original FastAPI | n8n equivalent |
|------------------|----------------|
| `POST /calls/outbound` | Workflow **outbound-initiate** (Webhook/Manual → HTTP Twilio) |
| `POST /webhooks/twilio/voice` & `/gather` | Workflow **voice-conversation** (Webhook → Postgres → Claude → Respond TwiML) |
| `POST /webhooks/twilio/status` | Workflow **call-status-finalize** (Webhook → Claude summarize → Postgres update) |
| `services/lead_scoring.py` | a **Code** node (same scoring formula, included in spec) |
| `services/claude_service.py` | **HTTP Request** node to `api.anthropic.com/v1/messages` |
| Dashboard (Next.js) | keep the original Next.js app **or** build n8n + a BI tool / Retool / Appsmith |

See `N8N_BUILD_SPEC.md` for the full build.

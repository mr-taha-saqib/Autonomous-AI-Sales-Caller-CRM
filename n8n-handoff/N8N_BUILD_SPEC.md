# N8N BUILD SPEC — Algorixe AI Caller

This is the authoritative, node-by-node build guide. Build the three workflows in order.
All of them share the same Postgres, Twilio, and Anthropic credentials.

---

## 0. Prerequisites & credentials (n8n → Settings → Credentials)

| Credential (n8n type) | Fields |
|-----------------------|--------|
| **Postgres** | host, port, db, user, password (from `schema.sql` instance) |
| **Twilio** (HTTP Basic Auth, or n8n Twilio cred) | Account SID + Auth Token |
| **Anthropic** (HTTP Header Auth) | Header `x-api-key: <ANTHROPIC_API_KEY>`, `anthropic-version: 2023-06-01` |

Public base URL for Twilio callbacks = your n8n instance URL, e.g.
`https://<your-n8n>/webhook/...`. Twilio **requires HTTPS**.

Models: `claude-opus-4-8` for live turns (low latency matters — you may prefer
`claude-sonnet-4-6` for snappier replies), `claude-sonnet-4-6` for extraction/summary.

---

## 1. Workflow A — `outbound-initiate`

**Goal:** start an AI call to a lead. Equivalent of `POST /calls/outbound`.

| # | Node | Type | Config |
|---|------|------|--------|
| 1 | **Start** | Webhook (POST `/initiate-call`) *or* Manual Trigger | body: `{ to_number, lead_id }` |
| 2 | **Insert call row** | Postgres → Insert | table `calls`; `direction='outbound'`, `status='queued'`, `from_number={{CALLER_ID}}`, `to_number`, `lead_id`. Return `id`. |
| 3 | **Create Twilio call** | HTTP Request (POST) | URL `https://api.twilio.com/2010-04-01/Accounts/{{SID}}/Calls.json`; Basic auth; form params: `To`, `From`, `Url=https://<n8n>/webhook/voice?call_id={{$json.id}}`, `StatusCallback=.../webhook/status?call_id={{id}}`, `StatusCallbackEvent=completed`, `Record=true`, `MachineDetection=DetectMessageEnd` |
| 4 | **Save SID** | Postgres → Update | set `calls.twilio_sid={{$json.sid}}`, `status='initiated'` where `id=call_id` |
| 5 | **Respond** | Respond to Webhook | `{ call_id, sid }` |

> Tip: to run **campaigns**, prepend a Postgres "Select hot leads" node + Split In Batches,
> and add a Wait node between calls for pacing/DNC windows.

---

## 2. Workflow B — `voice-conversation` (the core AI loop)

**Goal:** drive the live phone conversation. Equivalent of `/webhooks/twilio/voice` + `/gather`.
This workflow has **two webhook entry paths** (use one workflow with a Switch, or two workflows).

### 2a. Entry: `/voice` (call connects — speak the opening line)

| # | Node | Type | Config |
|---|------|------|--------|
| 1 | **Webhook /voice** | Webhook (POST), Respond = "Using Respond node" | query `call_id` |
| 2 | **Validate Twilio sig** *(optional but recommended)* | Code | verify `X-Twilio-Signature` (HMAC-SHA1 of URL+params with Auth Token); else 403 |
| 3 | **Get lead** | Postgres → Select | `leads` where `id` = call's `lead_id` (for the name) |
| 4 | **Build opening** | Set | `reply` = `Hi, this is the Algorixe Car Care sales team. Am I speaking with {{name}}?` (or the no-name variant) |
| 5 | **Seed transcript** | Postgres → Insert/Upsert | `transcripts(call_id, turns=[{role:'assistant',text:reply}])` |
| 6 | **Respond TwiML** | Respond to Webhook | Content-Type `text/xml`; body = Gather TwiML (see snippet below) |

### 2b. Entry: `/gather` (each customer utterance → Claude → reply)

| # | Node | Type | Config |
|---|------|------|--------|
| 1 | **Webhook /gather** | Webhook (POST) | query `call_id`; body has `SpeechResult` |
| 2 | **Get transcript** | Postgres → Select | `transcripts` where `call_id` |
| 3 | **Append user turn + build messages** | Code | push `{role:'user',text:SpeechResult}`; build Claude `messages` array (drop a leading assistant turn so first msg is `user`) |
| 4 | **Claude reply** | HTTP Request (POST) | `https://api.anthropic.com/v1/messages`; header-auth cred; JSON body: `model`, `max_tokens:1024`, `system={{system prompt from prompts.md}}`, `messages` |
| 5 | **Extract reply text** | Set/Code | `reply = $json.content[0].text` |
| 6 | **Persist turns** | Postgres → Update | append assistant turn to `transcripts.turns`, update `full_text` |
| 7 | **Hangup?** | IF | true if reply contains a farewell phrase ("thank you for your time", "goodbye", …) |
| 8a | **Respond (continue)** | Respond to Webhook | Gather TwiML with `reply` |
| 8b | **Respond (hangup)** | Respond to Webhook | `<Response><Say>{{reply}}</Say><Hangup/></Response>` |

### TwiML the Respond node returns (continue case)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="https://<n8n>/webhook/gather?call_id={{call_id}}"
          method="POST" speechTimeout="auto" speechModel="phone_call" language="en-US">
    <Say voice="Polly.Joanna-Neural">{{reply}}</Say>
  </Gather>
  <Redirect method="POST">https://<n8n>/webhook/voice?call_id={{call_id}}&amp;reprompt=1</Redirect>
</Response>
```

### Claude HTTP node — request body (JSON)

```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 1024,
  "temperature": 0.6,
  "system": "<<paste SYSTEM_PROMPT + OBJECTION_PLAYBOOK from prompts.md>>",
  "messages": {{ $json.messages }}
}
```

`messages` is `[{ "role":"user"|"assistant", "content":"..." }]`. **The first item must be
`role:"user"`** (the Code node strips a leading assistant turn or prepends `"(call connected)"`).

---

## 3. Workflow C — `call-status-finalize`

**Goal:** when the call completes, summarize + extract CRM fields + score the lead.
Equivalent of `/webhooks/twilio/status` + `services/conversation.finalize_call`.

| # | Node | Type | Config |
|---|------|------|--------|
| 1 | **Webhook /status** | Webhook (POST) | query `call_id`; body `CallStatus`, `CallDuration` |
| 2 | **Update call** | Postgres → Update | map `CallStatus`→our enum, set `duration_seconds` |
| 3 | **IF completed** | IF | continue only when `CallStatus == 'completed'` |
| 4 | **Get transcript** | Postgres → Select | full `turns` for `call_id` |
| 5 | **Render transcript text** | Code | "Agent: …\nCustomer: …" |
| 6 | **Claude summarize** | HTTP Request | messages API with **tool** `summarise_call` (tool_choice forced) → `{summary,key_intent,sentiment,outcome}` |
| 7 | **Claude extract** | HTTP Request | messages API with **tool** `record_lead` → `{full_name,email,location,budget,vehicle_interest,purchase_timeline,financing_need,trade_in_interest}` |
| 8 | **Score lead** | Code | run the scoring formula (below) → `score, temperature, conversion_probability` |
| 9 | **Upsert lead** | Postgres → Update/Insert | write extracted fields + score + status (`appointment_set`/`qualified`/`lost`/…) |
| 10 | **Update transcript+call** | Postgres → Update | save `summary,key_intent,sentiment,outcome` |
| 11 | **Respond 204** | Respond to Webhook | empty |

### Lead-scoring Code node (port of `lead_scoring.py`)

```javascript
// inputs: timeline, budget, vehicle, financing, tradeIn, email, sentiment
const TL = { 'immediate':35, '1-3 months':25, '3-6 months':12, 'researching':4 };
let s = 0;
const t = (timeline||'').toLowerCase();
for (const k in TL) if (t.includes(k)) { s += TL[k]; break; }
if (budget) s += 20;
if (vehicle) s += 15;
if (email) s += 8;
if (financing) s += 7;
if (tradeIn) s += 5;
if (sentiment === 'positive') s += 10; else if (sentiment === 'negative') s -= 10;
s = Math.max(0, Math.min(100, s));
const temperature = s >= 65 ? 'hot' : s >= 35 ? 'warm' : 'cold';
const conversion_probability = Math.min(0.95, Math.max(0.02, s/110));
return [{ json: { score: s, temperature, conversion_probability } }];
```

### Claude tool schema (for nodes 6 & 7)

Add `tools` + `tool_choice` to the HTTP body. Example for extraction:

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 512,
  "system": "You are a CRM data-extraction engine...",
  "tools": [{
    "name": "record_lead",
    "input_schema": { "type":"object", "properties": {
      "full_name":{"type":["string","null"]}, "email":{"type":["string","null"]},
      "location":{"type":["string","null"]}, "budget":{"type":["string","null"]},
      "vehicle_interest":{"type":["string","null"]},
      "purchase_timeline":{"type":["string","null"]},
      "financing_need":{"type":["boolean","null"]},
      "trade_in_interest":{"type":["boolean","null"]} } }
  }],
  "tool_choice": { "type":"tool", "name":"record_lead" },
  "messages": [{ "role":"user", "content": "{{transcriptText}}" }]
}
```

Read the result from `$json.content[].input` where `type === 'tool_use'`.

---

## 4. Inbound calls

Add a Twilio number whose **"A call comes in"** webhook points to a `/inbound` webhook in
n8n: insert an inbound `calls` row, seed a greeting transcript, and return the same Gather
TwiML — from there it reuses the `/gather` loop in Workflow B.

---

## 5. Appointments, CRM & dashboard

- **Appointments:** a small workflow (Webhook or n8n Form) → Postgres insert into
  `appointments` + set `leads.status='appointment_set'`. Optionally a **Google Calendar**
  node to create the event and a **Gmail/SMS** node to send confirmation.
- **CRM / analytics dashboard:** two clean options —
  1. **Keep the original Next.js dashboard** (already built & tested) pointed at the same
     Postgres — fastest path, zero rebuild.
  2. Build read views with **Retool/Appsmith/Metabase** on the same Postgres.
- **Reports:** a scheduled n8n workflow (Cron) → Postgres aggregate queries → email a daily/
  weekly summary (the SQL is in the original `docs/DATABASE.md`).

## 6. Security checklist (n8n)

- Validate the `X-Twilio-Signature` header on every Twilio webhook (Code node, HMAC-SHA1).
- Store all keys in n8n **Credentials**, never in node fields.
- Put n8n behind HTTPS; restrict the editor with auth/SSO.
- Respect DNC: skip leads where `leads.status='do_not_call'` or `customers.do_not_call=true`.
- Log every workflow run (n8n executions) — your audit trail equivalent of `activity_logs`.

## 7. Build order / acceptance test

1. Import `schema.sql`; create credentials.
2. Build **Workflow C** first (no telephony needed — feed it a fake transcript and confirm a lead gets scored).
3. Build **Workflow B**; test `/gather` with a manual POST (`SpeechResult=hello`) and confirm Claude replies + TwiML is returned.
4. Build **Workflow A**; place a real test call to a number you own.
5. End-to-end: call connects → AI converses → hangup → lead appears scored in Postgres → visible in the dashboard.

That's the whole system. The hard parts (prompts, scoring, schema, call flow) are pre-solved
in this folder — n8n just wires them together.

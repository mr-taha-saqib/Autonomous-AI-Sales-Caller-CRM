# User Guide — Algorixe Sales Console

## Signing in
Go to the dashboard URL and sign in with the email/password your admin created.
Toggle dark mode from the top bar.

## Dashboard
The home screen shows KPIs (leads, calls, appointments, conversion), the sales
funnel, lead-temperature breakdown, your hottest leads, and recent call activity.

## Lead Management
- **Search** by name, phone, or vehicle; **filter** by temperature.
- Each lead shows its **score** and **temperature** (🔴 hot / 🟠 warm / 🔵 cold),
  computed from timeline, budget, vehicle interest, financing and trade-in signals.
- Press **Call** to have the Algorixe Sales Assistant dial the lead immediately.

## Making an AI call
1. Find the lead and click **Call** (or `POST /api/v1/calls/outbound`).
2. The AI agent dials, greets the prospect, qualifies them, handles objections,
   and offers to book an appointment.
3. When the call ends, the transcript, summary, sentiment, intent and outcome are
   saved automatically, and the lead is re-scored.

## Call History
Browse every call. Click a row to open the full transcript, AI summary, sentiment,
intent and outcome. Recordings link out to Twilio where enabled.

## Appointments
View and manage showroom visits and virtual consultations. Update status
(scheduled → confirmed → completed / no-show) inline.

## CRM
Pick a contact to see their complete record — captured fields, AI intent summary,
and a running thread of **sales notes** you can add to.

## Analytics & Reports
- **Analytics**: trend charts for calls and new leads, funnel, and temperature mix;
  switch the period (daily/weekly/monthly).
- **Reports**: tabular KPI report you can **export as JSON**.

## The AI agent's behaviour
The assistant is professional, friendly and never pushy. It captures: name, email,
location, budget, vehicle interest, timeline, financing need and trade-in interest;
respects "not interested" and "do not call"; and always leaves the door open.

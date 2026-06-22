-- ============================================================================
-- Performance indexes for Algorixe Car Care CRM
-- ============================================================================

CREATE INDEX IF NOT EXISTS ix_users_email           ON users(email);
CREATE INDEX IF NOT EXISTS ix_customers_phone        ON customers(phone);
CREATE INDEX IF NOT EXISTS ix_customers_email        ON customers(email);

CREATE INDEX IF NOT EXISTS ix_leads_phone            ON leads(phone);
CREATE INDEX IF NOT EXISTS ix_leads_status           ON leads(status);
CREATE INDEX IF NOT EXISTS ix_leads_temperature      ON leads(temperature);
CREATE INDEX IF NOT EXISTS ix_leads_customer_id      ON leads(customer_id);
CREATE INDEX IF NOT EXISTS ix_leads_score            ON leads(score DESC);
-- Trigram search on key text fields (requires pg_trgm)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS ix_leads_fullname_trgm
    ON leads USING gin (full_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS ix_calls_twilio_sid       ON calls(twilio_sid);
CREATE INDEX IF NOT EXISTS ix_calls_status           ON calls(status);
CREATE INDEX IF NOT EXISTS ix_calls_lead_id          ON calls(lead_id);
CREATE INDEX IF NOT EXISTS ix_calls_created_at       ON calls(created_at DESC);

CREATE INDEX IF NOT EXISTS ix_appointments_sched     ON appointments(scheduled_for);
CREATE INDEX IF NOT EXISTS ix_appointments_status    ON appointments(status);
CREATE INDEX IF NOT EXISTS ix_appointments_rep       ON appointments(sales_rep_id);

CREATE INDEX IF NOT EXISTS ix_sales_notes_lead_id    ON sales_notes(lead_id);

CREATE INDEX IF NOT EXISTS ix_activity_logs_action   ON activity_logs(action);
CREATE INDEX IF NOT EXISTS ix_activity_logs_user_id  ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_activity_logs_created  ON activity_logs(created_at DESC);

-- JSONB transcript search
CREATE INDEX IF NOT EXISTS ix_transcripts_turns_gin
    ON transcripts USING gin (turns jsonb_path_ops);

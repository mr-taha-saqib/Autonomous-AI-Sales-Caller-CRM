-- ============================================================================
-- Algorixe Car Care — PostgreSQL schema (reference / manual provisioning)
-- The canonical source of truth is Alembic (backend/alembic). This file mirrors
-- it for DBAs and for environments provisioned without Python.
-- ============================================================================

BEGIN;

-- ---- Enum types ------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin','manager','agent','viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE lead_temperature AS ENUM ('hot','warm','cold');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE lead_status AS ENUM
        ('new','contacted','qualified','appointment_set','converted','lost','do_not_call');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE call_direction AS ENUM ('outbound','inbound');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE call_status AS ENUM
        ('queued','initiated','ringing','in_progress','completed','busy',
         'no_answer','failed','canceled','voicemail');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE appointment_type AS ENUM ('showroom_visit','virtual_consultation');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE appointment_status AS ENUM
        ('scheduled','confirmed','completed','canceled','no_show','rescheduled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---- Tables ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'agent',
    phone           VARCHAR(32),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS customers (
    id           SERIAL PRIMARY KEY,
    full_name    VARCHAR(120),
    phone        VARCHAR(32) NOT NULL UNIQUE,
    email        VARCHAR(255),
    location     VARCHAR(160),
    notes        TEXT,
    do_not_call  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS leads (
    id                     SERIAL PRIMARY KEY,
    customer_id            INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    full_name              VARCHAR(120),
    phone                  VARCHAR(32) NOT NULL,
    email                  VARCHAR(255),
    location               VARCHAR(160),
    budget                 VARCHAR(80),
    vehicle_interest       VARCHAR(160),
    purchase_timeline      VARCHAR(80),
    financing_need         BOOLEAN,
    trade_in_interest      BOOLEAN,
    score                  INTEGER NOT NULL DEFAULT 0,
    temperature            lead_temperature NOT NULL DEFAULT 'cold',
    status                 lead_status NOT NULL DEFAULT 'new',
    source                 VARCHAR(60) DEFAULT 'outbound_call',
    intent_summary         TEXT,
    sentiment              VARCHAR(20),
    conversion_probability DOUBLE PRECISION,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS calls (
    id               SERIAL PRIMARY KEY,
    twilio_sid       VARCHAR(64) UNIQUE,
    direction        call_direction NOT NULL,
    status           call_status NOT NULL DEFAULT 'queued',
    from_number      VARCHAR(32) NOT NULL,
    to_number        VARCHAR(32) NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    recording_url    VARCHAR(512),
    summary          TEXT,
    key_intent       VARCHAR(255),
    sentiment        VARCHAR(20),
    outcome          VARCHAR(60),
    customer_id      INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    lead_id          INTEGER REFERENCES leads(id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transcripts (
    id          SERIAL PRIMARY KEY,
    call_id     INTEGER NOT NULL UNIQUE REFERENCES calls(id) ON DELETE CASCADE,
    turns       JSONB NOT NULL DEFAULT '[]'::jsonb,
    full_text   TEXT,
    summary     TEXT,
    key_intent  VARCHAR(255),
    sentiment   VARCHAR(20),
    outcome     VARCHAR(60),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS appointments (
    id               SERIAL PRIMARY KEY,
    customer_id      INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    lead_id          INTEGER REFERENCES leads(id) ON DELETE SET NULL,
    sales_rep_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    appointment_type appointment_type NOT NULL DEFAULT 'showroom_visit',
    status           appointment_status NOT NULL DEFAULT 'scheduled',
    scheduled_for    TIMESTAMPTZ NOT NULL,
    location         VARCHAR(200),
    meeting_link     VARCHAR(400),
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sales_notes (
    id         SERIAL PRIMARY KEY,
    lead_id    INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    author_id  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    category   VARCHAR(40) DEFAULT 'general',
    body       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(80) NOT NULL,
    entity_type VARCHAR(40),
    entity_id   INTEGER,
    ip_address  VARCHAR(64),
    detail      JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMIT;

\i indexes.sql

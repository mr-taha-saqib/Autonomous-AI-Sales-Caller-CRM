"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts(table):
    table.append_column(sa.Column("created_at", sa.DateTime(timezone=True),
                                  server_default=sa.func.now(), nullable=False))
    table.append_column(sa.Column("updated_at", sa.DateTime(timezone=True),
                                  server_default=sa.func.now(), nullable=False))


def upgrade() -> None:
    user_role = sa.Enum("admin", "manager", "agent", "viewer", name="user_role")
    lead_temp = sa.Enum("hot", "warm", "cold", name="lead_temperature")
    lead_status = sa.Enum("new", "contacted", "qualified", "appointment_set",
                          "converted", "lost", "do_not_call", name="lead_status")
    call_dir = sa.Enum("outbound", "inbound", name="call_direction")
    call_status = sa.Enum("queued", "initiated", "ringing", "in_progress",
                          "completed", "busy", "no_answer", "failed", "canceled",
                          "voicemail", name="call_status")
    appt_type = sa.Enum("showroom_visit", "virtual_consultation",
                        name="appointment_type")
    appt_status = sa.Enum("scheduled", "confirmed", "completed", "canceled",
                          "no_show", "rescheduled", name="appointment_status")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="agent"),
        sa.Column("phone", sa.String(32)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("full_name", sa.String(120)),
        sa.Column("phone", sa.String(32), nullable=False, unique=True),
        sa.Column("email", sa.String(255)),
        sa.Column("location", sa.String(160)),
        sa.Column("notes", sa.Text),
        sa.Column("do_not_call", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_customers_phone", "customers", ["phone"])
    op.create_index("ix_customers_email", "customers", ["email"])

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer,
                  sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("full_name", sa.String(120)),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("location", sa.String(160)),
        sa.Column("budget", sa.String(80)),
        sa.Column("vehicle_interest", sa.String(160)),
        sa.Column("purchase_timeline", sa.String(80)),
        sa.Column("financing_need", sa.Boolean),
        sa.Column("trade_in_interest", sa.Boolean),
        sa.Column("score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("temperature", lead_temp, nullable=False, server_default="cold"),
        sa.Column("status", lead_status, nullable=False, server_default="new"),
        sa.Column("source", sa.String(60), server_default="outbound_call"),
        sa.Column("intent_summary", sa.Text),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("conversion_probability", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_leads_phone", "leads", ["phone"])
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_temperature", "leads", ["temperature"])
    op.create_index("ix_leads_customer_id", "leads", ["customer_id"])

    op.create_table(
        "calls",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("twilio_sid", sa.String(64), unique=True),
        sa.Column("direction", call_dir, nullable=False),
        sa.Column("status", call_status, nullable=False, server_default="queued"),
        sa.Column("from_number", sa.String(32), nullable=False),
        sa.Column("to_number", sa.String(32), nullable=False),
        sa.Column("duration_seconds", sa.Integer, server_default="0"),
        sa.Column("recording_url", sa.String(512)),
        sa.Column("summary", sa.Text),
        sa.Column("key_intent", sa.String(255)),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("outcome", sa.String(60)),
        sa.Column("customer_id", sa.Integer,
                  sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("lead_id", sa.Integer,
                  sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_calls_twilio_sid", "calls", ["twilio_sid"])
    op.create_index("ix_calls_status", "calls", ["status"])
    op.create_index("ix_calls_lead_id", "calls", ["lead_id"])

    op.create_table(
        "transcripts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("call_id", sa.Integer,
                  sa.ForeignKey("calls.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("turns", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("full_text", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("key_intent", sa.String(255)),
        sa.Column("sentiment", sa.String(20)),
        sa.Column("outcome", sa.String(60)),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("customer_id", sa.Integer,
                  sa.ForeignKey("customers.id", ondelete="SET NULL")),
        sa.Column("lead_id", sa.Integer,
                  sa.ForeignKey("leads.id", ondelete="SET NULL")),
        sa.Column("sales_rep_id", sa.Integer,
                  sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("appointment_type", appt_type, nullable=False,
                  server_default="showroom_visit"),
        sa.Column("status", appt_status, nullable=False, server_default="scheduled"),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location", sa.String(200)),
        sa.Column("meeting_link", sa.String(400)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_appointments_scheduled_for", "appointments", ["scheduled_for"])
    op.create_index("ix_appointments_status", "appointments", ["status"])

    op.create_table(
        "sales_notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lead_id", sa.Integer,
                  sa.ForeignKey("leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer,
                  sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("category", sa.String(40), server_default="general"),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_sales_notes_lead_id", "sales_notes", ["lead_id"])

    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer,
                  sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(40)),
        sa.Column("entity_id", sa.Integer),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("detail", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])


def downgrade() -> None:
    for tbl in ("activity_logs", "sales_notes", "appointments", "transcripts",
                "calls", "leads", "customers", "users"):
        op.drop_table(tbl)
    for enum in ("appointment_status", "appointment_type", "call_status",
                 "call_direction", "lead_status", "lead_temperature", "user_role"):
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)

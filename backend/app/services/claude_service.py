"""Claude API integration — conversation turns, extraction, summarisation.

Uses the Anthropic Messages API. Conversation memory is passed in as a list of
{"role": "user"|"assistant", "content": "..."} turns. Tool use is used for
structured CRM extraction so the model returns validated JSON.
"""
from __future__ import annotations

import json
from typing import Any

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.services.prompts import (
    EXTRACTION_SYSTEM,
    OBJECTION_PLAYBOOK,
    SUMMARY_SYSTEM,
    SYSTEM_PROMPT,
)

log = get_logger("claude")

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _client


# ── Tool schemas for structured output ──────────────────────────────────────

LEAD_EXTRACTION_TOOL = {
    "name": "record_lead",
    "description": "Record structured lead-qualification fields extracted from the call.",
    "input_schema": {
        "type": "object",
        "properties": {
            "full_name": {"type": ["string", "null"]},
            "email": {"type": ["string", "null"]},
            "location": {"type": ["string", "null"]},
            "budget": {"type": ["string", "null"]},
            "vehicle_interest": {"type": ["string", "null"]},
            "purchase_timeline": {
                "type": ["string", "null"],
                "description": "immediate | 1-3 months | 3-6 months | researching | unknown",
            },
            "financing_need": {"type": ["boolean", "null"]},
            "trade_in_interest": {"type": ["boolean", "null"]},
        },
        "required": [],
    },
}

CALL_SUMMARY_TOOL = {
    "name": "summarise_call",
    "description": "Summarise the sales call for the CRM.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_intent": {"type": "string"},
            "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
            "outcome": {
                "type": "string",
                "enum": [
                    "appointment_booked",
                    "callback_requested",
                    "not_interested",
                    "no_answer",
                    "needs_followup",
                    "qualified",
                    "do_not_call",
                ],
            },
        },
        "required": ["summary", "key_intent", "sentiment", "outcome"],
    },
}


# ── Live conversation ────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
def generate_reply(history: list[dict[str, str]], lead_context: str = "") -> str:
    """Produce the assistant's next spoken turn given the conversation history."""
    system = SYSTEM_PROMPT + "\n\n" + OBJECTION_PLAYBOOK
    if lead_context:
        system += f"\n\n# Known lead context\n{lead_context}"

    # The Messages API requires the first turn to be from the user. Our transcript
    # often begins with the assistant's opening line, so prepend a synthetic
    # connect marker (and collapse any leading assistant turns into it).
    messages = list(history)
    while messages and messages[0]["role"] == "assistant":
        messages.pop(0)
    if not messages:
        messages = [{"role": "user", "content": "(call connected — greet the customer)"}]
    elif messages[0]["role"] != "user":
        messages.insert(0, {"role": "user", "content": "(call connected)"})

    resp = get_client().messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=settings.CLAUDE_MAX_TOKENS,
        temperature=settings.CLAUDE_TEMPERATURE,
        system=system,
        messages=messages,
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return text.strip() or "I'm sorry, could you say that again?"


def _tool_call_result(resp: Any, tool_name: str) -> dict[str, Any]:
    for block in resp.content:
        if block.type == "tool_use" and block.name == tool_name:
            return dict(block.input)
    return {}


@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
def extract_lead_fields(transcript_text: str) -> dict[str, Any]:
    """Extract structured CRM lead fields from a full transcript."""
    if not transcript_text.strip():
        return {}
    resp = get_client().messages.create(
        model=settings.CLAUDE_FAST_MODEL,
        max_tokens=512,
        system=EXTRACTION_SYSTEM,
        tools=[LEAD_EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_lead"},
        messages=[{"role": "user", "content": transcript_text}],
    )
    return _tool_call_result(resp, "record_lead")


@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=0.5, min=0.5, max=4))
def summarise_call(transcript_text: str) -> dict[str, Any]:
    """Produce summary / intent / sentiment / outcome from a transcript."""
    if not transcript_text.strip():
        return {
            "summary": "No conversation captured.",
            "key_intent": "unknown",
            "sentiment": "neutral",
            "outcome": "no_answer",
        }
    resp = get_client().messages.create(
        model=settings.CLAUDE_FAST_MODEL,
        max_tokens=512,
        system=SUMMARY_SYSTEM,
        tools=[CALL_SUMMARY_TOOL],
        tool_choice={"type": "tool", "name": "summarise_call"},
        messages=[{"role": "user", "content": transcript_text}],
    )
    result = _tool_call_result(resp, "summarise_call")
    log.info("call_summarised", outcome=result.get("outcome"))
    return result


def transcript_to_text(turns: list[dict[str, Any]]) -> str:
    """Render JSON turns into a readable transcript for extraction/summary."""
    lines = []
    for t in turns:
        role = "Agent" if t.get("role") == "assistant" else "Customer"
        lines.append(f"{role}: {t.get('text', '')}")
    return "\n".join(lines)

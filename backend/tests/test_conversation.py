from unittest.mock import patch

from app.models.call import Call, CallDirection, CallStatus
from app.services import conversation


def _make_call(db):
    call = Call(
        direction=CallDirection.OUTBOUND, status=CallStatus.IN_PROGRESS,
        from_number="+15551234567", to_number="+15559990009",
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def test_next_turn_appends_and_replies(db_session):
    db, _ = db_session
    call = _make_call(db)
    with patch("app.services.conversation.claude_service.generate_reply",
               return_value="Great, what's your budget?"):
        reply, hangup = conversation.next_turn(db, call, "I'm looking for an SUV")
    assert reply == "Great, what's your budget?"
    assert hangup is False
    assert len(call.transcript.turns) == 2


def test_farewell_triggers_hangup(db_session):
    db, _ = db_session
    call = _make_call(db)
    with patch("app.services.conversation.claude_service.generate_reply",
               return_value="Thank you for your time, have a great day!"):
        _, hangup = conversation.next_turn(db, call, "not interested")
    assert hangup is True


def test_finalize_call_runs_summary_and_scoring(db_session):
    db, _ = db_session
    call = _make_call(db)
    t = conversation._get_or_create_transcript(db, call)
    t.turns = [
        {"role": "assistant", "text": "Hi, interested in a car?"},
        {"role": "user", "text": "Yes, an EV, budget 40k, buying this month"},
    ]
    db.commit()

    summary = {"summary": "Wants EV.", "key_intent": "Buy EV",
               "sentiment": "positive", "outcome": "qualified"}
    fields = {"vehicle_interest": "EV", "budget": "$40,000",
              "purchase_timeline": "immediate", "financing_need": True}

    with patch("app.services.conversation.claude_service.summarise_call",
               return_value=summary), \
         patch("app.services.conversation.claude_service.extract_lead_fields",
               return_value=fields):
        conversation.finalize_call(db, call)
        db.commit()

    assert call.outcome == "qualified"
    assert call.lead is not None
    assert call.lead.vehicle_interest == "EV"
    assert call.lead.score > 0

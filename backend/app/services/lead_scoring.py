"""Deterministic lead scoring → temperature (hot/warm/cold).

The score is an explainable 0-100 weighting over qualification signals. The model's
extracted fields feed in; analysts can audit exactly why a lead is hot.
"""
from __future__ import annotations

from app.models.lead import LeadTemperature

# Timeline → urgency points
_TIMELINE_POINTS = {
    "immediate": 35,
    "1-3 months": 25,
    "3-6 months": 12,
    "researching": 4,
    "unknown": 0,
}


def _timeline_points(timeline: str | None) -> int:
    if not timeline:
        return 0
    key = timeline.strip().lower()
    for k, v in _TIMELINE_POINTS.items():
        if k in key:
            return v
    return 0


def score_lead(
    *,
    purchase_timeline: str | None,
    budget: str | None,
    vehicle_interest: str | None,
    financing_need: bool | None,
    trade_in_interest: bool | None,
    email: str | None,
    sentiment: str | None = None,
) -> tuple[int, LeadTemperature, float]:
    """Return (score 0-100, temperature, conversion_probability 0-1)."""
    score = 0
    score += _timeline_points(purchase_timeline)

    if budget:
        score += 20
    if vehicle_interest:
        score += 15
    if email:
        score += 8
    if financing_need:
        score += 7
    if trade_in_interest:
        score += 5

    if sentiment == "positive":
        score += 10
    elif sentiment == "negative":
        score -= 10

    score = max(0, min(100, score))

    if score >= 65:
        temp = LeadTemperature.HOT
    elif score >= 35:
        temp = LeadTemperature.WARM
    else:
        temp = LeadTemperature.COLD

    # Simple logistic-ish mapping to a probability.
    probability = round(min(0.95, max(0.02, score / 110)), 3)
    return score, temp, probability

from app.models.lead import LeadTemperature
from app.services.lead_scoring import score_lead


def test_hot_lead():
    score, temp, prob = score_lead(
        purchase_timeline="immediate", budget="$45,000",
        vehicle_interest="EV sedan", financing_need=True,
        trade_in_interest=True, email="a@b.com", sentiment="positive",
    )
    assert temp == LeadTemperature.HOT
    assert score >= 65
    assert 0 < prob <= 0.95


def test_cold_lead():
    score, temp, _ = score_lead(
        purchase_timeline="researching", budget=None,
        vehicle_interest=None, financing_need=False,
        trade_in_interest=False, email=None, sentiment="negative",
    )
    assert temp == LeadTemperature.COLD
    assert score < 35


def test_warm_lead_in_range():
    score, temp, _ = score_lead(
        purchase_timeline="3-6 months", budget="£30,000",
        vehicle_interest="minivan", financing_need=True,
        trade_in_interest=False, email="t@b.com", sentiment="neutral",
    )
    assert temp == LeadTemperature.WARM
    assert 35 <= score < 65


def test_score_is_bounded():
    score, _, prob = score_lead(
        purchase_timeline="immediate", budget="x", vehicle_interest="x",
        financing_need=True, trade_in_interest=True, email="x@y.z",
        sentiment="positive",
    )
    assert 0 <= score <= 100
    assert prob <= 0.95

def test_dashboard_summary(client, auth_headers):
    res = client.get("/api/v1/analytics/summary", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    for key in ("total_leads", "total_calls", "lead_conversion_rate"):
        assert key in body


def test_funnel(client, auth_headers):
    res = client.get("/api/v1/analytics/funnel", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_report_periods(client, auth_headers):
    for period in ("daily", "weekly", "monthly"):
        res = client.get(f"/api/v1/analytics/reports/{period}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["period"] == period


def test_invalid_report_period(client, auth_headers):
    res = client.get("/api/v1/analytics/reports/yearly", headers=auth_headers)
    assert res.status_code == 400


def test_dashboard_home(client, auth_headers):
    res = client.get("/api/v1/dashboard/home", headers=auth_headers)
    assert res.status_code == 200
    assert "summary" in res.json()

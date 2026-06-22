from unittest.mock import patch


def test_outbound_call_places_via_twilio(client, auth_headers):
    with patch("app.api.routes.calls.twilio_service.place_outbound_call",
               return_value="CA_test_sid") as mock_place:
        res = client.post(
            "/api/v1/calls/outbound",
            json={"to_number": "+15558675309"},
            headers=auth_headers,
        )
    assert res.status_code == 201
    body = res.json()
    assert body["twilio_sid"] == "CA_test_sid"
    assert body["status"] == "initiated"
    mock_place.assert_called_once()


def test_outbound_call_handles_twilio_failure(client, auth_headers):
    with patch("app.api.routes.calls.twilio_service.place_outbound_call",
               side_effect=Exception("twilio down")):
        res = client.post(
            "/api/v1/calls/outbound",
            json={"to_number": "+15558675309"},
            headers=auth_headers,
        )
    assert res.status_code == 502


def test_list_calls_empty(client, auth_headers):
    res = client.get("/api/v1/calls", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["total"] == 0

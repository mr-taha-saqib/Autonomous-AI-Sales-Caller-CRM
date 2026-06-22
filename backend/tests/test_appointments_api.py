def _create_lead(client, auth_headers):
    return client.post("/api/v1/leads",
                       json={"phone": "+15557770001", "full_name": "Appt Lead"},
                       headers=auth_headers).json()


def test_create_appointment_marks_lead(client, auth_headers):
    lead = _create_lead(client, auth_headers)
    res = client.post(
        "/api/v1/appointments",
        json={
            "lead_id": lead["id"],
            "appointment_type": "showroom_visit",
            "scheduled_for": "2030-01-01T10:00:00Z",
            "location": "Main Showroom",
        },
        headers=auth_headers,
    )
    assert res.status_code == 201
    assert res.json()["status"] == "scheduled"

    lead_after = client.get(f"/api/v1/leads/{lead['id']}", headers=auth_headers).json()
    assert lead_after["status"] == "appointment_set"


def test_update_and_cancel_appointment(client, auth_headers):
    appt = client.post(
        "/api/v1/appointments",
        json={"appointment_type": "virtual_consultation",
              "scheduled_for": "2030-02-01T10:00:00Z"},
        headers=auth_headers,
    ).json()

    upd = client.patch(f"/api/v1/appointments/{appt['id']}",
                       json={"status": "confirmed"}, headers=auth_headers)
    assert upd.json()["status"] == "confirmed"

    cancel = client.delete(f"/api/v1/appointments/{appt['id']}", headers=auth_headers)
    assert cancel.status_code == 200

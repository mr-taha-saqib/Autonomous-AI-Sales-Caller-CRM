def test_create_and_list_lead(client, auth_headers):
    payload = {
        "phone": "+15559990001",
        "full_name": "Test Lead",
        "vehicle_interest": "Compact SUV",
        "purchase_timeline": "immediate",
        "budget": "$30,000",
        "email": "lead@test.com",
        "financing_need": True,
    }
    res = client.post("/api/v1/leads", json=payload, headers=auth_headers)
    assert res.status_code == 201
    created = res.json()
    assert created["temperature"] in ("hot", "warm", "cold")
    assert created["score"] > 0

    res = client.get("/api/v1/leads", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["total"] >= 1


def test_lead_search_filter(client, auth_headers):
    client.post("/api/v1/leads",
                json={"phone": "+15559990002", "full_name": "Searchable Person"},
                headers=auth_headers)
    res = client.get("/api/v1/leads?search=Searchable", headers=auth_headers)
    assert res.status_code == 200
    assert any("Searchable" in (i["full_name"] or "") for i in res.json()["items"])


def test_update_lead_rescores(client, auth_headers):
    lead = client.post("/api/v1/leads",
                       json={"phone": "+15559990003"},
                       headers=auth_headers).json()
    res = client.patch(
        f"/api/v1/leads/{lead['id']}",
        json={"purchase_timeline": "immediate", "budget": "$50k",
              "vehicle_interest": "EV", "financing_need": True},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["score"] > lead["score"]

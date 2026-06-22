def test_login_success(client):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "Password!123"},
    )
    assert res.status_code == 200
    body = res.json()
    assert "access_token" in body and "refresh_token" in body


def test_login_wrong_password(client):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "nope-wrong-1"},
    )
    assert res.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_user(client, auth_headers):
    res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "admin@test.com"


def test_token_refresh(client):
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "Password!123"},
    ).json()
    res = client.post("/api/v1/auth/refresh",
                      json={"refresh_token": login["refresh_token"]})
    assert res.status_code == 200
    assert "access_token" in res.json()

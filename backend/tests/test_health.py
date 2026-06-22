def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] in ("ok", "degraded")


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "name" in res.json()

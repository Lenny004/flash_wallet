"""Tests basicos de humo para la API Flash."""


def test_health(client):
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] in ("ok", "degraded")
    assert data["database"] in ("ok", "error")
    if data["database"] == "ok":
        assert response.status_code == 200
        assert data["status"] == "ok"
    else:
        assert data["status"] == "degraded"


def test_docs_disponible(client):
    response = client.get("/docs")
    assert response.status_code == 200

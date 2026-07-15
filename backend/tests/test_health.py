"""Tests basicos de humo para la API Flash."""


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_disponible(client):
    response = client.get("/docs")
    assert response.status_code == 200

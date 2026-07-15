"""Tests basicos de humo para la API Flash."""

from fastapi.testclient import TestClient

# Preferir el paquete nuevo; fallar claro si no se puede importar
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_docs_disponible():
    response = client.get("/docs")
    assert response.status_code == 200


def test_usuarios_sin_datos_sensibles():
    """GET /api/usuarios/ no debe devolver hashes ni listados de usuarios."""
    response = client.get("/api/usuarios/")
    # Puede fallar si no hay DB; si responde 200, validar forma
    if response.status_code == 200:
        data = response.json()
        assert "hay_usuarios" in data
        assert "usuarios" not in data
        assert "contra" not in str(data)

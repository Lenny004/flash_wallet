"""Tests de guards de autenticación sin depender de MySQL real."""

import io


def test_decode_qr_sin_token_retorna_401(client):
    response = client.post(
        "/api/decode_qr/",
        files={"qr_image": ("test.png", io.BytesIO(b"fake-image"), "image/png")},
    )
    assert response.status_code == 401


def test_procesar_pagos_sin_token_retorna_401(client):
    response = client.post("/api/transaccion/procesar_pagos")
    assert response.status_code == 401


def test_historial_delete_sin_token_retorna_401(client):
    response = client.post("/api/historial/delete", json={"id_historial": 1})
    assert response.status_code == 401


def test_movimientos_sin_token_401(client):
    response = client.get("/api/historial/movimientos")
    assert response.status_code == 401


def test_crear_transaccion_sin_intent_falla(client):
    """POST /crear exige token antes que exp/sig; sin auth → 401."""
    response = client.post(
        "/api/transaccion/crear",
        json={
            "fecha_transaccion": "2026-07-14",
            "hora_transaccion": "10:30:00",
            "monto": 100.0,
            "frecuencia": 1,
            "descripcion": "Test sin intent",
            "id_servicio": 1,
            "id_estado": 1,
        },
    )
    assert response.status_code == 401


def test_factura_delete_sin_token_retorna_401(client):
    response = client.post("/api/factura/delete", json={"id_factura": 1})
    assert response.status_code == 401


def test_usuarios_sin_datos_sensibles(client):
    """GET /api/usuarios/ no debe devolver hashes ni listados de usuarios."""
    response = client.get("/api/usuarios/")
    if response.status_code == 200:
        data = response.json()
        assert "hay_usuarios" in data
        assert "usuarios" not in data
        assert "contra" not in str(data)


def test_refresh_sin_body_retorna_422(client):
    response = client.post("/api/usuarios/refresh")
    assert response.status_code == 422


def test_refresh_token_invalido_retorna_401(client):
    response = client.post(
        "/api/usuarios/refresh",
        json={"refresh_token": "token-invalido"},
    )
    assert response.status_code == 401

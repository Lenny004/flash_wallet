"""Tests unitarios del servicio de payment intents QR."""

import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services.qr_intent import crear_intent, verificar_intent


def test_crear_intent_incluye_exp_y_sig():
    payload = {
        "id_servicio": 1,
        "monto": 150.0,
        "frecuencia": 1,
        "descripcion": "Pago mensual",
        "fecha": "2026-07-14",
        "hora": "10:30:00",
        "id_estado": 1,
    }
    intent = crear_intent(payload)

    assert intent["exp"] > int(time.time())
    assert len(intent["sig"]) == 64
    assert intent["monto"] == 150.0


def test_verificar_intent_valido():
    payload = {
        "id_servicio": 2,
        "monto": 99.5,
        "frecuencia": 3,
        "descripcion": "Servicio",
        "fecha": "2026-07-14",
        "hora": "12:00:00",
        "id_estado": 1,
    }
    intent = crear_intent(payload)
    verified = verificar_intent(intent)

    assert verified["id_servicio"] == 2
    assert verified["monto"] == 99.5


def test_verificar_intent_firma_incorrecta():
    payload = {
        "id_servicio": 1,
        "monto": 10.0,
        "frecuencia": 1,
        "descripcion": "Test",
        "exp": int(time.time()) + 300,
        "sig": "0" * 64,
    }
    with pytest.raises(HTTPException) as exc:
        verificar_intent(payload)
    assert exc.value.status_code == 400
    assert "firma" in exc.value.detail.lower()


def test_verificar_intent_expirado():
    payload = {
        "id_servicio": 1,
        "monto": 10.0,
        "frecuencia": 1,
        "descripcion": "Test",
        "fecha": "2026-07-14",
        "hora": "10:00:00",
        "id_estado": 1,
    }
    intent = crear_intent(payload)
    intent["exp"] = int(time.time()) - 1

    with patch("app.services.qr_intent._firmar", return_value=intent["sig"]):
        with pytest.raises(HTTPException) as exc:
            verificar_intent(intent)
    assert exc.value.status_code == 400
    assert "expirado" in exc.value.detail.lower()

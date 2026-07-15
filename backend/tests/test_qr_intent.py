"""Tests unitarios del servicio de payment intents QR (sin DB)."""

import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.services.qr_intent import crear_intent, verificar_intent

PAYLOAD_BASE = {
    "id_servicio": 1,
    "monto": 150.0,
    "frecuencia": 1,
    "descripcion": "Pago mensual",
    "fecha": "2026-07-14",
    "hora": "10:30:00",
    "id_estado": 1,
}


class TestQrIntentUnit:
    """crear_intent / verificar_intent con secret mockeado, sin MySQL."""

    def test_crear_intent_incluye_exp_y_sig(self):
        with patch("app.services.qr_intent.settings.secret_key", "unit-test-secret"):
            intent = crear_intent(PAYLOAD_BASE.copy())

        assert intent["exp"] > int(time.time())
        assert len(intent["sig"]) == 64
        assert intent["monto"] == 150.0
        assert intent["id_servicio"] == 1

    def test_verificar_intent_valido(self):
        with patch("app.services.qr_intent.settings.secret_key", "unit-test-secret"):
            intent = crear_intent(
                {
                    "id_servicio": 2,
                    "monto": 99.5,
                    "frecuencia": 3,
                    "descripcion": "Servicio",
                    "fecha": "2026-07-14",
                    "hora": "12:00:00",
                    "id_estado": 1,
                }
            )
            verified = verificar_intent(intent)

        assert verified["id_servicio"] == 2
        assert verified["monto"] == 99.5

    def test_verificar_intent_firma_incorrecta(self):
        payload = {
            "id_servicio": 1,
            "monto": 10.0,
            "frecuencia": 1,
            "descripcion": "Test",
            "exp": int(time.time()) + 300,
            "sig": "0" * 64,
        }
        with patch("app.services.qr_intent.settings.secret_key", "unit-test-secret"):
            with pytest.raises(HTTPException) as exc:
                verificar_intent(payload)
        assert exc.value.status_code == 400
        assert "firma" in exc.value.detail.lower()

    def test_verificar_intent_expirado(self):
        with patch("app.services.qr_intent.settings.secret_key", "unit-test-secret"):
            intent = crear_intent(PAYLOAD_BASE.copy())
            intent["exp"] = int(time.time()) - 1

            with patch("app.services.qr_intent._firmar", return_value=intent["sig"]):
                with pytest.raises(HTTPException) as exc:
                    verificar_intent(intent)
        assert exc.value.status_code == 400
        assert "expirado" in exc.value.detail.lower()

    def test_verificar_intent_campo_faltante(self):
        with patch("app.services.qr_intent.settings.secret_key", "unit-test-secret"):
            with pytest.raises(HTTPException) as exc:
                verificar_intent({"id_servicio": 1, "monto": 10.0})
        assert exc.value.status_code == 400
        assert "falta" in exc.value.detail.lower()

    def test_firma_depende_del_secret(self):
        with patch("app.services.qr_intent.settings.secret_key", "secret-a"):
            intent = crear_intent(PAYLOAD_BASE.copy())

        with patch("app.services.qr_intent.settings.secret_key", "secret-b"):
            with pytest.raises(HTTPException) as exc:
                verificar_intent(intent)
        assert exc.value.status_code == 400
        assert "firma" in exc.value.detail.lower()

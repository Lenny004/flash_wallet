"""Creación y verificación de intents QR firmados con HMAC."""

import hashlib
import hmac
import time

from fastapi import HTTPException

from app.core.config import settings


# --- Firma y canonicalización ---


def _canonical_string(
    id_servicio: int, monto: float, frecuencia: int, descripcion: str, exp: int
) -> str:
    """Serializa los campos del intent en un formato determinista."""
    return f"{id_servicio}|{monto}|{frecuencia}|{descripcion}|{exp}"


def _firmar(canonical: str) -> str:
    """Calcula la firma HMAC-SHA256 del string canónico."""
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# --- API pública ---


def crear_intent(payload: dict) -> dict:
    """Genera un intent QR con expiración y firma HMAC.

    Args:
        payload: Datos del servicio (``id_servicio``, ``monto``, ``frecuencia``,
            ``descripcion``).

    Returns:
        Payload original más ``exp`` y ``sig``.
    """
    exp = int(time.time()) + settings.qr_intent_ttl_seconds
    canonical = _canonical_string(
        payload["id_servicio"],
        payload["monto"],
        payload["frecuencia"],
        payload["descripcion"],
        exp,
    )
    return {
        **payload,
        "exp": exp,
        "sig": _firmar(canonical),
    }


def verificar_intent(data: dict) -> dict:
    """Valida campos, expiración y firma de un intent QR.

    Args:
        data: Intent recibido del cliente (incluye ``sig`` y ``exp``).

    Returns:
        Intent normalizado con tipos primitivos.

    Raises:
        HTTPException: 400 si falta un campo, expiró o la firma no coincide.
    """
    required = ("id_servicio", "monto", "frecuencia", "descripcion", "exp", "sig")
    for field in required:
        if field not in data or data[field] is None:
            raise HTTPException(status_code=400, detail=f"Intent inválido: falta {field}")

    exp = int(data["exp"])
    if time.time() > exp:
        raise HTTPException(status_code=400, detail="Intent expirado")

    canonical = _canonical_string(
        int(data["id_servicio"]),
        float(data["monto"]),
        int(data["frecuencia"]),
        str(data["descripcion"]),
        exp,
    )
    firma_esperada = _firmar(canonical)
    if not hmac.compare_digest(str(data["sig"]), firma_esperada):
        raise HTTPException(status_code=400, detail="Intent inválido: firma incorrecta")

    return {
        "id_servicio": int(data["id_servicio"]),
        "monto": float(data["monto"]),
        "frecuencia": int(data["frecuencia"]),
        "descripcion": str(data["descripcion"]),
        "exp": exp,
        "sig": str(data["sig"]),
    }

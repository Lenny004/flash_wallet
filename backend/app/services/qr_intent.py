import hashlib
import hmac
import time

from fastapi import HTTPException

from app.core.config import settings


def _canonical_string(id_servicio: int, monto: float, frecuencia: int, descripcion: str, exp: int) -> str:
    return f"{id_servicio}|{monto}|{frecuencia}|{descripcion}|{exp}"


def _firmar(canonical: str) -> str:
    return hmac.new(
        settings.secret_key.encode("utf-8"),
        canonical.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def crear_intent(payload: dict) -> dict:
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
    expected_sig = _firmar(canonical)
    if not hmac.compare_digest(str(data["sig"]), expected_sig):
        raise HTTPException(status_code=400, detail="Intent inválido: firma incorrecta")

    return {
        "id_servicio": int(data["id_servicio"]),
        "monto": float(data["monto"]),
        "frecuencia": int(data["frecuencia"]),
        "descripcion": str(data["descripcion"]),
        "exp": exp,
        "sig": str(data["sig"]),
    }

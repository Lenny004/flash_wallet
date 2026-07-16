"""Almacén en memoria de códigos de recuperación de contraseña.

Se pierde al reiniciar el proceso — aceptable mientras no haya SMTP/DB de tokens.
"""

from hashlib import sha256
from secrets import randbelow
from time import time

# email_normalizado -> {codigo_hash, expira_en, id_usuario}
_codigos: dict[str, dict[str, object]] = {}

TTL_SEGUNDOS = 15 * 60


def _hash_codigo(codigo: str) -> str:
    return sha256(codigo.encode("utf-8")).hexdigest()


def generar_codigo() -> str:
    """Genera un código numérico de 6 dígitos."""
    return f"{randbelow(1_000_000):06d}"


def guardar_codigo(email: str, codigo: str, id_usuario: int) -> None:
    """Guarda el hash del código asociado al email."""
    clave = email.strip().lower()
    _codigos[clave] = {
        "codigo_hash": _hash_codigo(codigo),
        "expira_en": time() + TTL_SEGUNDOS,
        "id_usuario": id_usuario,
    }


def consumir_codigo(email: str, codigo: str) -> int | None:
    """Valida y consume el código. Devuelve id_usuario o None si es inválido."""
    clave = email.strip().lower()
    entrada = _codigos.get(clave)
    if not entrada:
        return None
    if time() > float(entrada["expira_en"]):  # type: ignore[arg-type]
        _codigos.pop(clave, None)
        return None
    if entrada["codigo_hash"] != _hash_codigo(codigo):
        return None
    _codigos.pop(clave, None)
    return int(entrada["id_usuario"])  # type: ignore[arg-type]

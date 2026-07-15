"""Blacklist en memoria de refresh tokens revocados (por jti).

Se pierde al reiniciar el proceso — aceptable para v0.2; usar Redis/DB en producción.
"""

from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

_revoked_jtis: set[str] = set()


def _extract_jti(token: str) -> str | None:
    """Obtiene el ``jti`` del token sin validar expiración.

    Args:
        token: JWT del cual extraer el identificador.

    Returns:
        Valor de ``jti`` o ``None`` si el token no es decodificable.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
    except InvalidTokenError:
        return None
    return payload.get("jti")


def revoke(token: str) -> None:
    """Marca un refresh token como revocado (por jti).

    Args:
        token: JWT de refresh a invalidar.
    """
    jti = _extract_jti(token)
    if jti:
        _revoked_jtis.add(jti)


def is_revoked(token: str) -> bool:
    """Indica si el jti del token está en la blacklist.

    Args:
        token: JWT a comprobar.

    Returns:
        ``True`` si el token fue revocado.
    """
    jti = _extract_jti(token)
    if not jti:
        return False
    return jti in _revoked_jtis


def new_jti() -> str:
    """Genera un identificador único para un nuevo refresh token."""
    return uuid4().hex

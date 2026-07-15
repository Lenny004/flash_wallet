"""Blacklist en memoria de refresh tokens revocados (por jti).

Se pierde al reiniciar el proceso — aceptable para v0.2; usar Redis/DB en producción.
"""

from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

_revoked_jtis: set[str] = set()


def _extract_jti(token: str) -> str | None:
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
    """Marca un refresh token como revocado (por jti)."""
    jti = _extract_jti(token)
    if jti:
        _revoked_jtis.add(jti)


def is_revoked(token: str) -> bool:
    """True si el jti del token está en la blacklist."""
    jti = _extract_jti(token)
    if not jti:
        return False
    return jti in _revoked_jtis


def new_jti() -> str:
    return uuid4().hex

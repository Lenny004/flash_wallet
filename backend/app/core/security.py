from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException

from app.core.config import settings
from app.core.token_blacklist import is_revoked, new_jti


def crear_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def crear_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["type"] = "refresh"
    payload["jti"] = new_jti()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verificar_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido: no es un refresh token.")

    if not payload.get("idusuario"):
        raise HTTPException(status_code=401, detail="Token inválido: datos faltantes.")

    if is_revoked(token):
        raise HTTPException(status_code=401, detail="Token revocado.")

    return payload


def verificar_token_t(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado por autorizacion")

    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado JU")
    try:
        payload_tarjeta = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        if not payload_tarjeta.get("id_tarjeta"):
            raise HTTPException(status_code=401, detail="Token inválido: datos faltantes.")
        return payload_tarjeta
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")


def verificar_token_U(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    # Extraer el token del formato 'Bearer <token>'
    token = authorization.split(" ")[1] if authorization and authorization.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        # Decodificar el token y verificar la expiración
        payload_usuario = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload_usuario
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido.")

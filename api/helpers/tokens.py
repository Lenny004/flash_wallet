import jwt
from fastapi import Header, HTTPException

from helpers.config import settings


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
        if not payload_tarjeta.get("pan"):
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

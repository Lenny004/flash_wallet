from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_U
from app.api.routes.tarjeta import crear_tarjeta_usuario
from app.core.config import settings
from app.models.tarjeta import Tarjeta
from app.models.usuarios import Usuario
from app.schemas.usuario_schema import LoginRequest, UsuarioCreate, UsuarioUpdate

routerUsuario = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@routerUsuario.get("/")
def obtener_usuarios(db: Session = Depends(get_db)):
    """
    Indica si existen usuarios registrados (primer uso), sin exponer datos sensibles.
    """
    hay_usuarios = db.query(Usuario.id_usuario).first() is not None
    if not hay_usuarios:
        return {"estado": 0, "hay_usuarios": False, "exception": "No hay usuarios registrados."}
    return {"estado": 1, "hay_usuarios": True}


@routerUsuario.post("/")
def crear_usuario(body: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    if db.query(Usuario).filter((Usuario.email == body.email) | (Usuario.usuario == body.usuario)).first():
        raise HTTPException(status_code=400, detail="El email o el usuario ya están registrados.")

    contra_encriptada = pwd_context.hash(body.contra)
    nuevo_usuario = Usuario(
        nombres=body.nombres,
        apellidos=body.apellidos,
        direccion=body.direccion,
        telefono=body.telefono,
        email=body.email,
        usuario=body.usuario,
        contra=contra_encriptada,
        img_usuario=body.img_usuario,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    tarjeta = crear_tarjeta_usuario(nuevo_usuario.id_usuario, db)

    return {
        "estado": 1,
        "mensaje": "Usuario y tarjeta digital creados exitosamente.",
        "nuevo_usuario": {
            "id_usuario": nuevo_usuario.id_usuario,
            "nombres": nuevo_usuario.nombres,
            "apellidos": nuevo_usuario.apellidos,
            "usuario": nuevo_usuario.usuario,
        },
        "tarjeta": {
            "pan": tarjeta.pan,
            "cvc": tarjeta.cvc,
            "balance": tarjeta.balance,
            "fecha_creacion": tarjeta.fecha_creacion,
        },
    }


@routerUsuario.post("/login")
def login_usuario(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Verifica las credenciales del usuario.
    """
    usuario = db.query(Usuario).filter(Usuario.usuario == body.usuario).first()

    if not usuario or not pwd_context.verify(body.contra, usuario.contra):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload_usuario = {
        "idusuario": usuario.id_usuario,
        "usuario": usuario.usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "telefono": usuario.telefono,
        "direccion": usuario.direccion,
        "email": usuario.email,
        "exp": expira,
    }
    token_usuario = jwt.encode(
        payload_usuario, settings.secret_key, algorithm=settings.jwt_algorithm
    )

    tarjeta = db.query(Tarjeta).filter(Tarjeta.id_usuario == usuario.id_usuario).first()
    if not tarjeta:
        raise HTTPException(status_code=404, detail="No se encontró una tarjeta asociada a este usuario.")

    payload_tarjeta = {
        "id_tarjeta": tarjeta.id_tarjeta,
        "pan": tarjeta.pan,
        "fecha_creacion": tarjeta.fecha_creacion.isoformat(),
        "cvc": tarjeta.cvc,
        "nombres": usuario.nombres + " " + usuario.apellidos,
        "exp": expira,
    }
    token_tarjeta = jwt.encode(
        payload_tarjeta, settings.secret_key, algorithm=settings.jwt_algorithm
    )

    return {
        "estado": 1,
        "mensaje": "Inicio de sesión exitoso.",
        "token_usuario": token_usuario,
        "token_tarjeta": token_tarjeta,
    }


@routerUsuario.get("/readOne")
def obtener_usuarios(datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Obtiene los datos del usuario que ingresó en el login, basado en el token JWT.
    """
    if not datos_usuario:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    usuario = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()

    return {
        "estado": 1,
        "id_usuario": datos_usuario.get("idusuario"),
        "usuario": datos_usuario.get("usuario"),
        "nombres": datos_usuario.get("nombres"),
        "apellidos": datos_usuario.get("apellidos"),
        "telefono": usuario.telefono,
        "direccion": usuario.direccion,
        "email": usuario.email,
    }


@routerUsuario.put("/update")
def actualizar_usuario(body: UsuarioUpdate, datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Actualiza los datos de un usuario existente en la base de datos.
    """
    if not datos_usuario:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    usuario = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe.")

    if body.direccion is not None:
        usuario.direccion = body.direccion
    if body.telefono is not None:
        usuario.telefono = body.telefono
    if body.email is not None:
        if db.query(Usuario).filter(
            Usuario.email == body.email, Usuario.id_usuario != datos_usuario.get("idusuario")
        ).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario.")
        usuario.email = body.email

    db.commit()
    db.refresh(usuario)

    return {
        "estado": 1,
        "mensaje": "Usuario actualizado exitosamente.",
        "usuario_actualizado": {
            "id_usuario": usuario.id_usuario,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "usuario": usuario.usuario,
            "email": usuario.email,
            "telefono": usuario.telefono,
            "direccion": usuario.direccion,
            "img_usuario": usuario.img_usuario,
        },
    }

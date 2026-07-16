from fastapi import APIRouter, Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_U
from app.api.routes.tarjeta import crear_tarjeta_usuario
from app.core.password_reset import consumir_codigo, generar_codigo, guardar_codigo
from app.core.rate_limit import rate_limit
from app.core.security import crear_access_token, crear_refresh_token, verificar_refresh_token
from app.core.token_blacklist import revoke
from app.models.tarjeta import Tarjeta
from app.models.usuarios import Usuario
from app.schemas.usuario_schema import (
    ForgotPasswordRequest,
    HayUsuariosResponse,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    UsuarioCreate,
    UsuarioUpdate,
)

routerUsuario = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@routerUsuario.get("/", response_model=HayUsuariosResponse)
def obtener_usuarios(db: Session = Depends(get_db)):
    """
    Indica si existen usuarios registrados (primer uso), sin exponer datos sensibles.
    Auth: no requerida.
    """
    hay_usuarios = db.query(Usuario.id_usuario).first() is not None
    if not hay_usuarios:
        return {"estado": 0, "hay_usuarios": False, "exception": "No hay usuarios registrados."}
    return {"estado": 1, "hay_usuarios": True}


@routerUsuario.post("/")
def crear_usuario(body: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario y crea su tarjeta digital asociada.
    Auth: no requerida.
    """
    if db.query(Usuario).filter((Usuario.email == body.email) | (Usuario.usuario == body.usuario)).first():
        raise HTTPException(status_code=400, detail="El email o el usuario ya están registrados.")

    contrasena_encriptada = pwd_context.hash(body.contra)
    nuevo_usuario = Usuario(
        nombres=body.nombres,
        apellidos=body.apellidos,
        direccion=body.direccion,
        telefono=body.telefono,
        email=body.email,
        usuario=body.usuario,
        contra=contrasena_encriptada,
        img_usuario=body.img_usuario,
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    tarjeta_creada = crear_tarjeta_usuario(nuevo_usuario.id_usuario, db)

    return {
        "estado": 1,
        "mensaje": "Usuario y tarjeta digital creados exitosamente.",
        "nuevo_usuario": {
            "id_usuario": nuevo_usuario.id_usuario,
            "nombres": nuevo_usuario.nombres,
            "apellidos": nuevo_usuario.apellidos,
            "usuario": nuevo_usuario.usuario,
        },
        # CVC en claro solo aquí (una vez) para tarjeta_digital.html tras el registro.
        # GET /api/tarjeta/readOne devuelve cvc enmascarado ("***").
        "tarjeta": {
            "pan": tarjeta_creada.pan,
            "cvc": tarjeta_creada.cvc,
            "balance": tarjeta_creada.balance,
            "fecha_creacion": tarjeta_creada.fecha_creacion,
        },
    }


@routerUsuario.post("/login", response_model=None)
def login_usuario(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """
    Valida credenciales y devuelve tokens de acceso (usuario, tarjeta) y refresh.
    Auth: no requerida (rate limit por IP).
    """
    ip_cliente = request.client.host if request.client else "unknown"
    rate_limit(f"login:{ip_cliente}", limit=5, window=60)

    usuario_encontrado = db.query(Usuario).filter(Usuario.usuario == body.usuario).first()

    if not usuario_encontrado or not pwd_context.verify(body.contra, usuario_encontrado.contra):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    tarjeta_asociada = db.query(Tarjeta).filter(Tarjeta.id_usuario == usuario_encontrado.id_usuario).first()
    if not tarjeta_asociada:
        raise HTTPException(status_code=404, detail="No se encontró una tarjeta asociada a este usuario.")

    token_usuario = crear_access_token(
        {
            "idusuario": usuario_encontrado.id_usuario,
            "usuario": usuario_encontrado.usuario,
            "nombres": usuario_encontrado.nombres,
            "apellidos": usuario_encontrado.apellidos,
            "telefono": usuario_encontrado.telefono,
            "direccion": usuario_encontrado.direccion,
            "email": usuario_encontrado.email,
        }
    )
    token_tarjeta = crear_access_token(
        {
            "id_tarjeta": tarjeta_asociada.id_tarjeta,
            "nombres": usuario_encontrado.nombres + " " + usuario_encontrado.apellidos,
        }
    )
    refresh_token = crear_refresh_token({"idusuario": usuario_encontrado.id_usuario})

    return {
        "estado": 1,
        "mensaje": "Inicio de sesión exitoso.",
        "token_usuario": token_usuario,
        "token_tarjeta": token_tarjeta,
        "refresh_token": refresh_token,
    }


@routerUsuario.post("/refresh", response_model=None)
def refresh_tokens(body: RefreshRequest, db: Session = Depends(get_db)):
    """
    Renueva los access tokens de usuario y tarjeta usando un refresh token válido.
    Auth: no requerida (solo refresh token en el body).
    """
    payload = verificar_refresh_token(body.refresh_token)
    id_usuario = payload["idusuario"]

    usuario_encontrado = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")

    tarjeta_asociada = db.query(Tarjeta).filter(Tarjeta.id_usuario == id_usuario).first()
    if not tarjeta_asociada:
        raise HTTPException(status_code=404, detail="No se encontró una tarjeta asociada a este usuario.")

    token_usuario = crear_access_token(
        {
            "idusuario": usuario_encontrado.id_usuario,
            "usuario": usuario_encontrado.usuario,
            "nombres": usuario_encontrado.nombres,
            "apellidos": usuario_encontrado.apellidos,
            "telefono": usuario_encontrado.telefono,
            "direccion": usuario_encontrado.direccion,
            "email": usuario_encontrado.email,
        }
    )
    token_tarjeta = crear_access_token(
        {
            "id_tarjeta": tarjeta_asociada.id_tarjeta,
            "nombres": usuario_encontrado.nombres + " " + usuario_encontrado.apellidos,
        }
    )

    return {
        "estado": 1,
        "mensaje": "Tokens renovados exitosamente.",
        "token_usuario": token_usuario,
        "token_tarjeta": token_tarjeta,
    }


@routerUsuario.post("/logout", response_model=None)
def logout_usuario(body: RefreshRequest):
    """
    Revoca el refresh token añadiéndolo a la blacklist en memoria.
    Auth: no requerida (solo refresh token en el body).
    """
    revoke(body.refresh_token)
    return {"estado": 1, "mensaje": "Sesión cerrada correctamente."}


@routerUsuario.get("/readOne")
def obtener_usuario_actual(datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Devuelve los datos del usuario autenticado según el token JWT.
    Auth: requerida (token de usuario).
    """
    if not datos_usuario:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    usuario_encontrado = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()

    return {
        "estado": 1,
        "id_usuario": datos_usuario.get("idusuario"),
        "usuario": datos_usuario.get("usuario"),
        "nombres": datos_usuario.get("nombres"),
        "apellidos": datos_usuario.get("apellidos"),
        "telefono": usuario_encontrado.telefono,
        "direccion": usuario_encontrado.direccion,
        "email": usuario_encontrado.email,
    }


@routerUsuario.put("/update")
def actualizar_usuario(body: UsuarioUpdate, datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Actualiza dirección, teléfono y email del usuario autenticado.
    Auth: requerida (token de usuario).
    """
    if not datos_usuario:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    usuario_encontrado = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()

    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="El usuario no existe.")

    if body.direccion is not None:
        usuario_encontrado.direccion = body.direccion
    if body.telefono is not None:
        usuario_encontrado.telefono = body.telefono
    if body.email is not None:
        if db.query(Usuario).filter(
            Usuario.email == body.email, Usuario.id_usuario != datos_usuario.get("idusuario")
        ).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario.")
        usuario_encontrado.email = body.email

    db.commit()
    db.refresh(usuario_encontrado)

    return {
        "estado": 1,
        "mensaje": "Usuario actualizado exitosamente.",
        "usuario_actualizado": {
            "id_usuario": usuario_encontrado.id_usuario,
            "nombres": usuario_encontrado.nombres,
            "apellidos": usuario_encontrado.apellidos,
            "usuario": usuario_encontrado.usuario,
            "email": usuario_encontrado.email,
            "telefono": usuario_encontrado.telefono,
            "direccion": usuario_encontrado.direccion,
            "img_usuario": usuario_encontrado.img_usuario,
        },
    }


@routerUsuario.post("/forgot-password")
def solicitar_recuperacion(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Genera un código de recuperación para el email indicado.
    Auth: no requerida (rate limit por IP).

    Sin SMTP configurado, el código se devuelve en la respuesta para completar el flujo.
    El mensaje genérico evita filtrar si el correo existe cuando no se genera código.
    """
    ip_cliente = request.client.host if request.client else "unknown"
    rate_limit(f"forgot:{ip_cliente}", limit=5, window=60)

    mensaje_generico = (
        "Si el correo está registrado, recibirás un código para restablecer tu contraseña."
    )
    usuario_encontrado = db.query(Usuario).filter(Usuario.email == body.email).first()
    if not usuario_encontrado:
        return {"estado": 1, "mensaje": mensaje_generico}

    codigo = generar_codigo()
    guardar_codigo(body.email, codigo, usuario_encontrado.id_usuario)

    return {
        "estado": 1,
        "mensaje": (
            f"{mensaje_generico} "
            "Aún no hay envío de correo: usa el código mostrado (válido 15 minutos)."
        ),
        "codigo": codigo,
        "expira_minutos": 15,
    }


@routerUsuario.post("/reset-password")
def restablecer_contrasena(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Restablece la contraseña con el código de verificación.
    Auth: no requerida (rate limit por IP).
    """
    ip_cliente = request.client.host if request.client else "unknown"
    rate_limit(f"reset:{ip_cliente}", limit=5, window=60)

    if not body.codigo.isdigit():
        raise HTTPException(status_code=400, detail="El código debe ser numérico de 6 dígitos.")

    id_usuario = consumir_codigo(body.email, body.codigo)
    if id_usuario is None:
        raise HTTPException(status_code=400, detail="Código inválido o expirado.")

    usuario_encontrado = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    usuario_encontrado.contra = pwd_context.hash(body.nueva_contra)
    db.commit()

    return {
        "estado": 1,
        "mensaje": "Contraseña actualizada correctamente. Ya puedes iniciar sesión.",
    }

from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from helpers.database import get_db
from helpers.tokens import verificar_token_U
from helpers.config import settings
from models.usuarios import Usuario
from models.tarjeta import Tarjeta
from schemas.usuario_schema import UsuarioCreate, LoginRequest, UsuarioUpdate
from private.api_tarjeta import crear_tarjeta_usuario
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone

# Crear un router para agrupar endpoints relacionados con usuarios
routerUsuario = APIRouter()
# Configurar el contexto para encriptar y verificar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@routerUsuario.get("/")
def obtener_usuarios(db: Session = Depends(get_db)):
    """
    Obtiene todos los usuarios registrados en la base de datos(PRIMER USO).
    """
    usuarios = db.query(Usuario).all()
    if not usuarios:
        return {"estado": 0, "exception": "No hay usuarios registrados."}  # Cambié el estado a 0 para indicar que hubo un error
    return {"estado": 1, "usuarios": usuarios}


@routerUsuario.post("/")
def crear_usuario(body: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la base de datos.
    """
    # Verificar si el email o el usuario ya están registrados
    if db.query(Usuario).filter((Usuario.email == body.email) | (Usuario.usuario == body.usuario)).first():
        raise HTTPException(status_code=400, detail="El email o el usuario ya están registrados.")
    
    # Encriptar la contraseña
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
    
    # Agregar y guardar el usuario
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    # Crear la tarjeta asociada al nuevo usuario
    tarjeta = crear_tarjeta_usuario(nuevo_usuario.id_usuario, db)  # Llamamos a la función compartida para crear la tarjeta

    # Retornar solo los datos relevantes
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
        }
    }


@routerUsuario.post("/login")
def login_usuario(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Verifica las credenciales del usuario.
    """
    usuario = db.query(Usuario).filter(Usuario.usuario == body.usuario).first()

    if not usuario or not pwd_context.verify(body.contra, usuario.contra):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    #Configuramos el token JWT
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload_usuario  = {
        "idusuario": usuario.id_usuario,
        "usuario": usuario.usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "telefono": usuario.telefono,
        "direccion": usuario.direccion,
        "email": usuario.email,
        "exp": expira
    }
    token_usuario = jwt.encode(
        payload_usuario, settings.secret_key, algorithm=settings.jwt_algorithm
    )

    # Crear el token para la tarjeta
    tarjeta = db.query(Tarjeta).filter(Tarjeta.id_usuario == usuario.id_usuario).first()
    if not tarjeta:
        raise HTTPException(status_code=404, detail="No se encontró una tarjeta asociada a este usuario.")

    payload_tarjeta = {
        "id_tarjeta": tarjeta.id_tarjeta,
        "pan": tarjeta.pan,
        "fecha_creacion": tarjeta.fecha_creacion.isoformat(),
        "cvc": tarjeta.cvc,
        "nombres": usuario.nombres + " " + usuario.apellidos,
        "exp": expira
    }
    token_tarjeta = jwt.encode(
        payload_tarjeta, settings.secret_key, algorithm=settings.jwt_algorithm
    )

    return {
    "estado": 1,
    "mensaje": "Inicio de sesión exitoso.",
    "token_usuario": token_usuario,
    "token_tarjeta": token_tarjeta
    }


@routerUsuario.get("/readOne")
def obtener_usuarios(datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Obtiene los datos del usuario que ingresó en el login, basado en el token JWT.
    """
    if not datos_usuario:  # Asegúrate de que los datos del token estén presentes
        return {"estado": 0, "exception": "Token inválido o expirado."}  # Devuelve un estado 0 en caso de error
    
    # Buscar al usuario en la base de datos
    usuario = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()

    return {
        "estado": 1,
        "id_usuario": datos_usuario.get("idusuario"),
        "usuario": datos_usuario.get("usuario"),
        "nombres": datos_usuario.get("nombres"),
        "apellidos": datos_usuario.get("apellidos"),
        "telefono": usuario.telefono,
        "direccion": usuario.direccion,
        "email": usuario.email
    }


@routerUsuario.put("/update")
def actualizar_usuario(body: UsuarioUpdate, datos_usuario=Depends(verificar_token_U), db: Session = Depends(get_db)):
    """
    Actualiza los datos de un usuario existente en la base de datos.
    """
    if not datos_usuario:  # Asegúrate de que los datos del token estén presentes
        return {"estado": 0, "exception": "Token inválido o expirado."}  # Devuelve un estado 0 en caso de error
    
    # Buscar al usuario en la base de datos
    usuario = db.query(Usuario).filter(Usuario.id_usuario == datos_usuario.get("idusuario")).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe.")

    # Actualizar los campos proporcionados en el cuerpo de la solicitud
    if body.direccion is not None:
        usuario.direccion = body.direccion
    if body.telefono is not None:
        usuario.telefono = body.telefono
    if body.email is not None:
        # Verificar si el nuevo email ya está registrado por otro usuario
        if db.query(Usuario).filter(Usuario.email == body.email, Usuario.id_usuario != datos_usuario.get("idusuario")).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario.")
        usuario.email = body.email

    # Guardar los cambios
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
        }
    }


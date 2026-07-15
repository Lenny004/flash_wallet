from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from helpers.database import get_db  # Tu dependencia para obtener la sesión de la base de datos
from helpers.tokens import verificar_token_t
from models.usuarios import Usuario
from models.tarjeta import Tarjeta  # Asegúrate de importar tu modelo de SQLAlchemy para la tarjeta
import random

routerTarjeta = APIRouter()

def crear_tarjeta_usuario(id_usuario: int, db: Session):
    """
    Crea una tarjeta digital asociada a un usuario ya registrado.
    """
    # Lista para almacenar los números generados
    pan_code = ""
    cvc_code = random.randint(100, 999)

    # Generar 5 números enteros aleatorios entre 1 y 100
    for i in range(4):
        numero = random.randint(1000, 9999)
        if i < 3:
            pan_code += (str(numero) + " ")
        else:
            pan_code += (str(numero))

    # Verificar si el id_usuario existe en la base de datos
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Crear la tarjeta digital
    tarjeta = Tarjeta(
        pan= pan_code,  # Aquí generas el PAN real
        cvc= cvc_code,  # Aquí generas el CVC real
        balance=0.00,  # El balance inicial de la tarjeta
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now(),
        id_usuario=id_usuario
    )

    # Guardar la tarjeta en la base de datos
    db.add(tarjeta)
    db.commit()
    db.refresh(tarjeta)

    return tarjeta


@routerTarjeta.get("/readOne")
def obtener_tarjeta(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Obtiene los datos de la tarjeta luego del login, basado en el token JWT.
    """
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
    
    balance_db = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == datos_tarjeta.get('id_tarjeta')).first()

    return {
        "estado": 1,
        "pan": datos_tarjeta.get('pan'),  # Accede como un diccionario
        "fecha_creacion": datos_tarjeta.get('fecha_creacion'),
        "cvc": datos_tarjeta.get('cvc'),
        "nombre": datos_tarjeta.get('nombres'),
        "balance": float(balance_db.balance)
    }

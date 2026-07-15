import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.models.tarjeta import Tarjeta
from app.models.usuarios import Usuario

routerTarjeta = APIRouter()


def crear_tarjeta_usuario(id_usuario: int, db: Session):
    """
    Crea una tarjeta digital asociada a un usuario ya registrado.
    """
    pan_code = ""
    cvc_code = random.randint(100, 999)

    for i in range(4):
        numero = random.randint(1000, 9999)
        if i < 3:
            pan_code += str(numero) + " "
        else:
            pan_code += str(numero)

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tarjeta = Tarjeta(
        pan=pan_code,
        cvc=cvc_code,
        balance=0.00,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now(),
        id_usuario=id_usuario,
    )

    db.add(tarjeta)
    db.commit()
    db.refresh(tarjeta)

    return tarjeta


@routerTarjeta.get("/readOne")
def obtener_tarjeta(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Obtiene los datos de la tarjeta luego del login, basado en el token JWT.
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    balance_db = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == datos_tarjeta.get("id_tarjeta")).first()

    return {
        "estado": 1,
        "pan": datos_tarjeta.get("pan"),
        "fecha_creacion": datos_tarjeta.get("fecha_creacion"),
        "cvc": datos_tarjeta.get("cvc"),
        "nombre": datos_tarjeta.get("nombres"),
        "balance": float(balance_db.balance),
    }

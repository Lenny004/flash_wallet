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
    numero_pan = ""
    codigo_cvc = random.randint(100, 999)

    for indice_bloque in range(4):
        bloque_pan = random.randint(1000, 9999)
        if indice_bloque < 3:
            numero_pan += str(bloque_pan) + " "
        else:
            numero_pan += str(bloque_pan)

    usuario_encontrado = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tarjeta_nueva = Tarjeta(
        pan=numero_pan,
        cvc=codigo_cvc,
        balance=0.00,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now(),
        id_usuario=id_usuario,
    )

    db.add(tarjeta_nueva)
    db.commit()
    db.refresh(tarjeta_nueva)

    return tarjeta_nueva


@routerTarjeta.get("/readOne")
def obtener_tarjeta(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Devuelve los datos de la tarjeta digital del usuario autenticado (PAN, saldo).
    El CVC se devuelve enmascarado por seguridad; solo se expone en claro al registrar.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    tarjeta_encontrada = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == datos_tarjeta.get("id_tarjeta")).first()
    if not tarjeta_encontrada:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada.")

    return {
        "estado": 1,
        "pan": tarjeta_encontrada.pan,
        "fecha_creacion": tarjeta_encontrada.fecha_creacion,
        "cvc": "***",
        "nombre": datos_tarjeta.get("nombres"),
        "balance": float(tarjeta_encontrada.balance),
    }

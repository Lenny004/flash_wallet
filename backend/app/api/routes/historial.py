from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.models.historial import Historial
from app.models.movimiento import Movimiento
from app.schemas.historial_schema import BuscarHistorialRequest, EliminarHistorial, TablaHistorial
from app.schemas.movimiento_schema import TablaMovimiento
from app.services.wallet import recargar_saldo
routerHistorial = APIRouter()


@routerHistorial.get("/read")
def obtener_historial(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Lista todos los registros de depósito (historial) de la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    registros_historial = db.query(Historial).filter(Historial.id_tarjeta == datos_tarjeta.get("id_tarjeta")).all()
    if not registros_historial:
        return {"estado": 0, "exception": "No hay registros de historial de deposito."}

    historial_respuesta = [
        TablaHistorial(
            id_historial=registro.id_historial,
            monto_agregado=float(registro.monto_agregado),
            fecha_historial=registro.fecha_historial,
            hora_historial=registro.hora_historial,
            id_tarjeta=registro.id_tarjeta,
        )
        for registro in registros_historial
    ]

    return {"estado": 1, "dataset": historial_respuesta}


@routerHistorial.get("/movimientos")
def obtener_movimientos(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Lista los movimientos de saldo de la tarjeta autenticada, más recientes primero.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    movimientos_tarjeta = (
        db.query(Movimiento)
        .filter(Movimiento.id_tarjeta == datos_tarjeta.get("id_tarjeta"))
        .order_by(Movimiento.creado_en.desc())
        .all()
    )

    dataset = [
        TablaMovimiento(
            id_movimiento=movimiento.id_movimiento,
            id_tarjeta=movimiento.id_tarjeta,
            tipo=movimiento.tipo,
            monto=float(movimiento.monto),
            saldo_anterior=float(movimiento.saldo_anterior),
            saldo_nuevo=float(movimiento.saldo_nuevo),
            referencia=movimiento.referencia,
            creado_en=movimiento.creado_en,
        )
        for movimiento in movimientos_tarjeta
    ]

    return {"estado": 1, "dataset": dataset}


@routerHistorial.post("/buscar")
def buscar_historial(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Busca un registro de historial por monto exacto en la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    monto_buscado = Decimal(str(body.monto_agregado))
    registro_encontrado = (
        db.query(Historial)
        .filter(
            Historial.id_tarjeta == datos_tarjeta.get("id_tarjeta"),
            Historial.monto_agregado == monto_buscado,
        )
        .first()
    )

    if registro_encontrado:
        resultado = {
            "id_historial": registro_encontrado.id_historial,
            "monto_agregado": registro_encontrado.monto_agregado,
            "fecha_historial": registro_encontrado.fecha_historial,
            "hora_historial": registro_encontrado.hora_historial,
            "id_tarjeta": registro_encontrado.id_tarjeta,
        }
        return {"estado": 1, "mensaje": "Registro encontrado arbol", "dataset": [resultado]}

    raise HTTPException(
        status_code=404,
        detail="No se encontraron registros que coincidan con los criterios de búsqueda en el árbol.",
    )


@routerHistorial.post("/recargar")
def recargar(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Recarga saldo en la tarjeta digital autenticada y registra el depósito en historial.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    recargar_saldo(db, datos_tarjeta.get("id_tarjeta"), body.monto_agregado)

    return {"estado": True, "mensaje": "Recarga exitosa."}


@routerHistorial.post("/delete")
def eliminar_historial(body: EliminarHistorial, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Elimina un registro de historial de depósito por su ID en la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    id_historial = body.id_historial
    if not id_historial:
        raise HTTPException(status_code=400, detail="ID del historial no proporcionado.")

    try:
        registro_historial = db.query(Historial).filter(
            Historial.id_historial == id_historial,
            Historial.id_tarjeta == id_tarjeta,
        ).first()

        if not registro_historial:
            raise HTTPException(status_code=404, detail="Historial de deposito no encontrado.")

        db.delete(registro_historial)
        db.commit()
        return {"estado": 1, "message": "Historial de deposito eliminado correctamente."}
    except Exception as error:
        db.rollback()
        print(f"Error al eliminar el historial: {error}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar el historial: {str(error)}")

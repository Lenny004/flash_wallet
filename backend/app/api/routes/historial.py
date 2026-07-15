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
    Obtiene todos los registros de historial de la tarjeta actual en la base de datos.
    """
    if not datos_tarjeta:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    historial = db.query(Historial).filter(Historial.id_tarjeta == datos_tarjeta.get("id_tarjeta")).all()
    if not historial:
        return {"estado": 0, "exception": "No hay registros de historial de deposito."}

    historial_response = [
        TablaHistorial(
            id_historial=h.id_historial,
            monto_agregado=float(h.monto_agregado),
            fecha_historial=h.fecha_historial,
            hora_historial=h.hora_historial,
            id_tarjeta=h.id_tarjeta,
        )
        for h in historial
    ]

    return {"estado": 1, "dataset": historial_response}


@routerHistorial.get("/movimientos")
def obtener_movimientos(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Lista los movimientos de saldo de la tarjeta actual, más recientes primero.
    """
    if not datos_tarjeta:
        return {"estado": 0, "exception": "Token inválido o expirado."}

    movimientos = (
        db.query(Movimiento)
        .filter(Movimiento.id_tarjeta == datos_tarjeta.get("id_tarjeta"))
        .order_by(Movimiento.creado_en.desc())
        .all()
    )

    dataset = [
        TablaMovimiento(
            id_movimiento=m.id_movimiento,
            id_tarjeta=m.id_tarjeta,
            tipo=m.tipo,
            monto=float(m.monto),
            saldo_anterior=float(m.saldo_anterior),
            saldo_nuevo=float(m.saldo_nuevo),
            referencia=m.referencia,
            creado_en=m.creado_en,
        )
        for m in movimientos
    ]

    return {"estado": 1, "dataset": dataset}


@routerHistorial.post("/buscar")
def buscar_historial(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Permite buscar los registros de historial según el monto_agregado
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    monto = Decimal(str(body.monto_agregado))
    historial = (
        db.query(Historial)
        .filter(
            Historial.id_tarjeta == datos_tarjeta.get("id_tarjeta"),
            Historial.monto_agregado == monto,
        )
        .first()
    )

    if historial:
        resultado = {
            "id_historial": historial.id_historial,
            "monto_agregado": historial.monto_agregado,
            "fecha_historial": historial.fecha_historial,
            "hora_historial": historial.hora_historial,
            "id_tarjeta": historial.id_tarjeta,
        }
        return {"estado": 1, "mensaje": "Registro encontrado arbol", "dataset": [resultado]}

    raise HTTPException(
        status_code=404,
        detail="No se encontraron registros que coincidan con los criterios de búsqueda en el árbol.",
    )


@routerHistorial.post("/recargar")
def recargar(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Actualiza el monto de la tarjeta digital actual del usuario
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    recargar_saldo(db, datos_tarjeta.get("id_tarjeta"), body.monto_agregado)

    return {"estado": True, "mensaje": "Recarga exitosa."}


@routerHistorial.post("/delete")
def eliminar_historial(body: EliminarHistorial, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Elimina un historial específico por su ID.
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    idhistorial = body.id_historial
    if not idhistorial:
        raise HTTPException(status_code=400, detail="ID del historial no proporcionado.")

    try:
        historial = db.query(Historial).filter(
            Historial.id_historial == idhistorial,
            Historial.id_tarjeta == id_tarjeta,
        ).first()

        if not historial:
            raise HTTPException(status_code=404, detail="Historial de deposito no encontrado.")

        db.delete(historial)
        db.commit()
        return {"estado": 1, "message": "Historial de deposito eliminado correctamente."}
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar el historial: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar el historial: {str(e)}")

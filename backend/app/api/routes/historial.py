from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.helpers.arbol_binario import ArbolBinarioBusqueda
from app.models.historial import Historial
from app.models.tarjeta import Tarjeta
from app.schemas.historial_schema import BuscarHistorialRequest, EliminarHistorial, TablaHistorial

routerHistorial = APIRouter()
arbol = ArbolBinarioBusqueda()


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


@routerHistorial.post("/buscar")
def buscar_historial(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Permite buscar los registros de historial según el monto_agregado
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    monto = body.monto_agregado
    historial = db.query(Historial).filter(Historial.id_tarjeta == datos_tarjeta.get("id_tarjeta")).all()
    for h in historial:
        arbol.insertar(
            h.monto_agregado,
            {
                "id_historial": h.id_historial,
                "monto_agregado": h.monto_agregado,
                "fecha_historial": h.fecha_historial,
                "hora_historial": h.hora_historial,
                "id_tarjeta": h.id_tarjeta,
            },
        )

    resultado_en_arbol = arbol.buscar(monto)
    if resultado_en_arbol:
        return {"estado": 1, "mensaje": "Registro encontrado arbol", "dataset": [resultado_en_arbol]}
    else:
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

    tarjeta = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == datos_tarjeta.get("id_tarjeta")).first()

    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    tarjeta.balance = tarjeta.balance + Decimal(str(body.monto_agregado))
    tarjeta.fecha_actualizacion = datetime.now()

    db.commit()
    db.refresh(tarjeta)

    historial = Historial(
        monto_agregado=body.monto_agregado,
        fecha_historial=datetime.now().date(),
        hora_historial=datetime.now().time(),
        id_tarjeta=datos_tarjeta.get("id_tarjeta"),
    )
    db.add(historial)
    db.commit()

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

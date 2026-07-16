from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from helpers.database import get_db
from helpers.tokens import verificar_token_t
from models.historial import Historial
from models.tarjeta import Tarjeta
from schemas.historial_schema import TablaHistorial, BuscarHistorialRequest, EliminarHistorial
from datetime import datetime
from decimal import Decimal

# Creamos la ruta del router
routerHistorial = APIRouter()

@routerHistorial.get("/read")
def obtener_historial(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Obtiene todos los registros de historial de la tarjeta actual en la base de datos.
    """
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        return {"estado": 0, "exception": "Token inválido o expirado."}  # Devuelve un estado 0 en caso de error

    historial = db.query(Historial).filter(Historial.id_tarjeta == datos_tarjeta.get('id_tarjeta')).all()
    if not historial:
        return {"estado": 0, "exception": "No hay registros de historial de deposito."}  # Devuelve un estado 0 si no hay historial
    
    # Mapeo de los objetos Historial a diccionarios para la respuesta
    historial_response = [
        TablaHistorial(
            id_historial=h.id_historial,
            monto_agregado=float(h.monto_agregado),
            fecha_historial=h.fecha_historial,
            hora_historial=h.hora_historial,
            id_tarjeta=h.id_tarjeta
        ) for h in historial
    ]
    
    return {"estado": 1, "dataset": historial_response}


@routerHistorial.post("/buscar")
def buscar_historial(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Permite buscar los registros de historial según el monto_agregado
    """
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
    
    monto = Decimal(str(body.monto_agregado))
    historial = (
        db.query(Historial)
        .filter(
            Historial.id_tarjeta == datos_tarjeta.get('id_tarjeta'),
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

    raise HTTPException(status_code=404, detail="No se encontraron registros que coincidan con los criterios de búsqueda en el árbol.")


@routerHistorial.post("/recargar")
def recargar(body: BuscarHistorialRequest, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Actualiza el monto de la tarjeta digital actual del usuario
    """
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    tarjeta = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == datos_tarjeta.get('id_tarjeta')).first()
        
    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")
    
    # Actualizar el balance y la fecha de actualización
    tarjeta.balance = tarjeta.balance + Decimal(str(body.monto_agregado))
    tarjeta.fecha_actualizacion = datetime.now()


    # Guardar los cambios en la base de datos
    db.commit()
    db.refresh(tarjeta)  # Refresca el objeto para asegurarte de que esté actualizado
    
    # Registrar el historial
    historial = Historial(
        monto_agregado=body.monto_agregado,
        fecha_historial=datetime.now().date(),
        hora_historial=datetime.now().time(),
        id_tarjeta=datos_tarjeta.get('id_tarjeta'),
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

    id_tarjeta = datos_tarjeta.get('id_tarjeta')
    idhistorial = body.id_historial
    if not idhistorial:
        raise HTTPException(status_code=400, detail="ID del historial no proporcionado.")
    
    try:
        # Buscar el historial en la base de datos y validar que pertenezca a la tarjeta del token
        historial = db.query(Historial).filter(
            Historial.id_historial == idhistorial,
            Historial.id_tarjeta == id_tarjeta
        ).first()
        
        if not historial:
            raise HTTPException(status_code=404, detail="Historial de deposito no encontrado.")
        
        # Eliminar el historial
        db.delete(historial)
        db.commit()
        return {"estado": 1, "message": "Historial de deposito eliminado correctamente."}
    except Exception as e:
        db.rollback()  # Revertir cambios en caso de error
        print(f"Error al eliminar el historial: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar el historial: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.models.factura import Factura
from app.models.servicio import Servicio
from app.models.tarjeta import Tarjeta
from app.models.transaccion import Transaccion
from app.schemas.factura_schema import BuscarFactura, EliminarFactura

routerFactura = APIRouter()


@routerFactura.get("/read")
def obtener_facturas(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Lista todas las facturas emitidas para la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")

    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    consulta_facturas = (
        db.query(
            Factura.id_factura,
            Factura.fecha_factura,
            Factura.hora_factura,
            Factura.monto_total,
            Servicio.nombre.label("nombre_servicio"),
        )
        .join(Transaccion, Factura.id_transaccion == Transaccion.id_transaccion)
        .join(Servicio, Transaccion.id_servicio == Servicio.id_servicio)
        .join(Tarjeta, Transaccion.id_tarjeta == Tarjeta.id_tarjeta)
        .filter(Tarjeta.id_tarjeta == id_tarjeta)
    )

    try:
        filas_resultado = consulta_facturas.all()

        if not filas_resultado:
            return {"estado": 0, "detail": "No se encontraron facturas."}

        facturas_respuesta = [
            {
                "id_factura": fila.id_factura,
                "fecha_factura": str(fila.fecha_factura),
                "hora_factura": str(fila.hora_factura),
                "monto_total": float(fila.monto_total),
                "nombre_servicio": fila.nombre_servicio,
            }
            for fila in filas_resultado
        ]

        return {"estado": 1, "dataset": facturas_respuesta}

    except Exception as error:
        print(f"Error al obtener las facturas: {error}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(error)}")


@routerFactura.post("/buscar")
def buscar_factura(body: BuscarFactura, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Busca una factura por nombre de servicio en la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    try:
        fila_factura = (
            db.query(
                Factura.id_factura,
                Factura.fecha_factura,
                Factura.hora_factura,
                Factura.monto_total,
                Servicio.nombre.label("nombre_servicio"),
            )
            .join(Transaccion, Factura.id_transaccion == Transaccion.id_transaccion)
            .join(Servicio, Transaccion.id_servicio == Servicio.id_servicio)
            .join(Tarjeta, Transaccion.id_tarjeta == Tarjeta.id_tarjeta)
            .filter(
                Tarjeta.id_tarjeta == id_tarjeta,
                Servicio.nombre.ilike(body.nombre),
            )
            .first()
        )

        if fila_factura:
            factura_encontrada = {
                "id_factura": fila_factura.id_factura,
                "fecha_factura": str(fila_factura.fecha_factura),
                "hora_factura": str(fila_factura.hora_factura),
                "monto_total": float(fila_factura.monto_total),
                "nombre_servicio": fila_factura.nombre_servicio,
            }
            return {"estado": 1, "mensaje": "Registro encontrado en el árbol.", "dataset": [factura_encontrada]}

        raise HTTPException(status_code=404, detail="No se encontraron registros que coincidan en el árbol.")

    except Exception as error:
        print(f"Error al obtener las facturas: {error}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(error)}")


@routerFactura.post("/delete")
def eliminar_factura(body: EliminarFactura, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Elimina una factura por su ID en la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    id_factura = body.id_factura
    if not id_factura:
        raise HTTPException(status_code=400, detail="ID de factura no proporcionado.")

    try:
        factura_registro = (
            db.query(Factura)
            .join(Transaccion, Factura.id_transaccion == Transaccion.id_transaccion)
            .filter(Factura.id_factura == id_factura, Transaccion.id_tarjeta == id_tarjeta)
            .first()
        )

        if not factura_registro:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")

        db.delete(factura_registro)
        db.commit()
        return {"estado": 1, "message": "Factura eliminada correctamente."}
    except Exception as error:
        db.rollback()
        print(f"Error al eliminar la factura: {error}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar la factura: {str(error)}")

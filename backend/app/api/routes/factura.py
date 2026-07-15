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
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    idtarjeta = datos_tarjeta.get("id_tarjeta")

    if not idtarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    query = (
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
        .filter(Tarjeta.id_tarjeta == idtarjeta)
    )

    try:
        result = query.all()

        if not result:
            return {"estado": 0, "detail": "No se encontraron facturas."}

        facturas = [
            {
                "id_factura": row.id_factura,
                "fecha_factura": str(row.fecha_factura),
                "hora_factura": str(row.hora_factura),
                "monto_total": float(row.monto_total),
                "nombre_servicio": row.nombre_servicio,
            }
            for row in result
        ]

        return {"estado": 1, "dataset": facturas}

    except Exception as e:
        print(f"Error al obtener las facturas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")


@routerFactura.post("/buscar")
def buscar_factura(body: BuscarFactura, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Busca una factura específica por el nombre del servicio.
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    idtarjeta = datos_tarjeta.get("id_tarjeta")
    if not idtarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    try:
        resultado = (
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
                Tarjeta.id_tarjeta == idtarjeta,
                Servicio.nombre.ilike(body.nombre),
            )
            .first()
        )

        if resultado:
            factura = {
                "id_factura": resultado.id_factura,
                "fecha_factura": str(resultado.fecha_factura),
                "hora_factura": str(resultado.hora_factura),
                "monto_total": float(resultado.monto_total),
                "nombre_servicio": resultado.nombre_servicio,
            }
            return {"estado": 1, "mensaje": "Registro encontrado en el árbol.", "dataset": [factura]}

        raise HTTPException(status_code=404, detail="No se encontraron registros que coincidan en el árbol.")

    except Exception as e:
        print(f"Error al obtener las facturas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")


@routerFactura.post("/delete")
def eliminar_factura(body: EliminarFactura, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Elimina una factura específica por su ID.
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    idfactura = body.id_factura
    if not idfactura:
        raise HTTPException(status_code=400, detail="ID de factura no proporcionado.")

    try:
        factura = (
            db.query(Factura)
            .join(Transaccion, Factura.id_transaccion == Transaccion.id_transaccion)
            .filter(Factura.id_factura == idfactura, Transaccion.id_tarjeta == id_tarjeta)
            .first()
        )

        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")

        db.delete(factura)
        db.commit()
        return {"estado": 1, "message": "Factura eliminada correctamente."}
    except Exception as e:
        db.rollback()
        print(f"Error al eliminar la factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar la factura: {str(e)}")

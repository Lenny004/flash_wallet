from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from helpers.database import get_db
from helpers.tokens import verificar_token_t
from helpers.arbol_binario import ArbolBinarioBusqueda
from models.factura import Factura
from schemas.factura_schema import EliminarFactura, CrearFacturaRequest, BuscarFactura
from models.transaccion import Transaccion
from models.servicio import Servicio
import datetime
from models.tarjeta import Tarjeta

routerFactura = APIRouter()
arbol = ArbolBinarioBusqueda()

@routerFactura.get("/read")
def obtener_facturas(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    idtarjeta = datos_tarjeta.get("id_tarjeta")
    
    if not idtarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    # Realizando la consulta con SQLAlchemy
    query = db.query(
        Factura.id_factura,
        Factura.fecha_factura,
        Factura.hora_factura,
        Factura.monto_total,
        Servicio.nombre.label("nombre_servicio")
    ).join(
        Transaccion, Factura.id_transaccion == Transaccion.id_transaccion
    ).join(
        Servicio, Transaccion.id_servicio == Servicio.id_servicio
    ).join(
        Tarjeta, Transaccion.id_tarjeta == Tarjeta.id_tarjeta
    ).filter(
        Tarjeta.id_tarjeta == idtarjeta
    )

    try:
        # Ejecutar la consulta y obtener los resultados
        result = query.all()
        
        # Si no hay resultados, enviar mensaje adecuado
        if not result:
            return {"estado": 0, "detail": "No se encontraron facturas."}

        # Formatear los resultados usando KeyedTuple (por nombre)
        facturas = [
            {
                "id_factura": row.id_factura,
                "fecha_factura": str(row.fecha_factura),
                "hora_factura": str(row.hora_factura),
                "monto_total": float(row.monto_total),
                "nombre_servicio": row.nombre_servicio
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
        # Realizando la consulta con SQLAlchemy
        query = db.query(
            Factura.id_factura,
            Factura.fecha_factura,
            Factura.hora_factura,
            Factura.monto_total,
            Servicio.nombre.label("nombre_servicio")
        ).join(
            Transaccion, Factura.id_transaccion == Transaccion.id_transaccion
        ).join(
            Servicio, Transaccion.id_servicio == Servicio.id_servicio
        ).join(
            Tarjeta, Transaccion.id_tarjeta == Tarjeta.id_tarjeta
        ).filter(
            Tarjeta.id_tarjeta == idtarjeta
        )

        # Insertar datos al árbol binario
        for f in query.all():
            arbol.insertar(f.nombre_servicio, {
                "id_factura": f.id_factura,
                "fecha_factura": str(f.fecha_factura),
                "hora_factura": str(f.hora_factura),
                "monto_total": float(f.monto_total),
                "nombre_servicio": f.nombre_servicio
            })

        # Buscar en el árbol
        resultado = arbol.buscar(body.nombre)
        if resultado:
            return {"estado": 1, "mensaje": "Registro encontrado en el árbol.", "dataset": [resultado]}

        # Si no se encuentra en el árbol
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
        # Buscar la factura validando que pertenezca a una transacción de la tarjeta del token
        factura = db.query(Factura).join(
            Transaccion, Factura.id_transaccion == Transaccion.id_transaccion
        ).filter(
            Factura.id_factura == idfactura,
            Transaccion.id_tarjeta == id_tarjeta
        ).first()
        
        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")
        
        # Eliminar la factura
        db.delete(factura)
        db.commit()
        return {"estado": 1, "message": "Factura eliminada correctamente."}
    except Exception as e:
        db.rollback()  # Revertir cambios en caso de error
        print(f"Error al eliminar la factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar la factura: {str(e)}")


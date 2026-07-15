from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.core.enums import EstadoTransaccion
from app.models.estado import Estado
from app.models.servicio import Servicio
from app.models.transaccion import Transaccion
from app.schemas.transaccion_schema import TransaccionDesdeIntent
from app.services.payments_worker import procesar_pagos_tarjeta
from app.services.qr_intent import verificar_intent

routerTransaccion = APIRouter()


@routerTransaccion.get("/read")
def obtener_facturas(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    idtarjeta = datos_tarjeta.get("id_tarjeta")

    if not idtarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    query = (
        db.query(
            Transaccion.id_transaccion,
            Transaccion.fecha_transaccion,
            Transaccion.hora_transaccion,
            Transaccion.monto,
            Transaccion.frecuencia,
            Transaccion.descripcion,
            Transaccion.id_estado,
            Estado.estado.label("estado"),
            Servicio.nombre.label("nombre"),
        )
        .join(Estado, Transaccion.id_estado == Estado.id_estado)
        .join(Servicio, Transaccion.id_servicio == Servicio.id_servicio)
        .filter(
            and_(
                Transaccion.id_tarjeta == idtarjeta,
                Transaccion.id_estado != EstadoTransaccion.COMPLETADA,
            )
        )
    )

    try:
        result = query.all()

        if not result:
            return {"estado": 0, "detail": "No se encontraron transacciones."}

        transaccion = [
            {
                "id_transaccion": row.id_transaccion,
                "fecha_transaccion": str(row.fecha_transaccion),
                "hora_transaccion": str(row.hora_transaccion),
                "monto": float(row.monto),
                "frecuencia": float(row.frecuencia),
                "descripcion": str(row.descripcion),
                "id_estado": row.id_estado,
                "estado": str(row.estado),
                "nombre": str(row.nombre),
            }
            for row in result
        ]

        return {"estado": 1, "dataset": transaccion}

    except Exception as e:
        print(f"Error al obtener las facturas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")


@routerTransaccion.post("/crear")
def crear_transaccion(body: TransaccionDesdeIntent, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Crea una nueva transacción en la base de datos.
    Requiere un payment intent firmado obtenido al escanear el QR.
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    try:
        intent = verificar_intent(
            {
                "id_servicio": body.id_servicio,
                "monto": body.monto,
                "frecuencia": body.frecuencia,
                "descripcion": body.descripcion,
                "exp": body.exp,
                "sig": body.sig,
            }
        )

        nueva_transaccion = Transaccion(
            fecha_transaccion=body.fecha_transaccion,
            hora_transaccion=body.hora_transaccion,
            monto=intent["monto"],
            frecuencia=intent["frecuencia"],
            descripcion=intent["descripcion"],
            id_tarjeta=datos_tarjeta.get("id_tarjeta"),
            id_servicio=intent["id_servicio"],
            id_estado=body.id_estado,
        )

        db.add(nueva_transaccion)
        db.commit()
        db.refresh(nueva_transaccion)

        return {"estado": 1, "mensaje": "Transacción creada exitosamente."}

    except KeyError as ke:
        print(f"Error de clave faltante: {ke}")
        raise HTTPException(status_code=422, detail=f"Falta el campo obligatorio: {ke}")
    except ValueError as ve:
        print(f"Error de conversión: {ve}")
        raise HTTPException(status_code=422, detail="Error en el formato de los datos enviados.")
    except ValidationError as e:
        print(f"Errores de validación: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno en el servidor.")


@routerTransaccion.post("/procesar_pagos")
def procesar_pagos(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    procesar_pagos_tarjeta(db, id_tarjeta)
    return {"estado": 1, "mensaje": "Pagos procesados correctamente."}


@routerTransaccion.get("/saldo_pendiente")
def saldo_pendiente(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    transacciones_pendientes = db.query(Transaccion).filter(
        Transaccion.id_tarjeta == datos_tarjeta.get("id_tarjeta"),
        Transaccion.id_estado == EstadoTransaccion.FALLIDO,
    ).all()

    monto_pendiente = sum([transaccion.monto for transaccion in transacciones_pendientes])

    return {
        "estado": 1,
        "mensaje": f"El monto pendiente de recargar es {monto_pendiente:.2f} unidades monetarias.",
        "monto_pendiente": monto_pendiente,
    }

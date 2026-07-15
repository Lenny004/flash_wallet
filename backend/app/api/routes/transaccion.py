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
def obtener_transacciones(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Lista las transacciones pendientes (no completadas) de la tarjeta autenticada.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")

    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    consulta_transacciones = (
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
                Transaccion.id_tarjeta == id_tarjeta,
                Transaccion.id_estado != EstadoTransaccion.COMPLETADA,
            )
        )
    )

    try:
        filas_resultado = consulta_transacciones.all()

        if not filas_resultado:
            return {"estado": 0, "detail": "No se encontraron transacciones."}

        transacciones_respuesta = [
            {
                "id_transaccion": fila.id_transaccion,
                "fecha_transaccion": str(fila.fecha_transaccion),
                "hora_transaccion": str(fila.hora_transaccion),
                "monto": float(fila.monto),
                "frecuencia": float(fila.frecuencia),
                "descripcion": str(fila.descripcion),
                "id_estado": fila.id_estado,
                "estado": str(fila.estado),
                "nombre": str(fila.nombre),
            }
            for fila in filas_resultado
        ]

        return {"estado": 1, "dataset": transacciones_respuesta}

    except Exception as error:
        print(f"Error al obtener las facturas: {error}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(error)}")


@routerTransaccion.post("/crear")
def crear_transaccion(body: TransaccionDesdeIntent, datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Crea una transacción validando un payment intent firmado obtenido al escanear un QR.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    try:
        intent_verificado = verificar_intent(
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
            monto=intent_verificado["monto"],
            frecuencia=intent_verificado["frecuencia"],
            descripcion=intent_verificado["descripcion"],
            id_tarjeta=datos_tarjeta.get("id_tarjeta"),
            id_servicio=intent_verificado["id_servicio"],
            id_estado=body.id_estado,
        )

        db.add(nueva_transaccion)
        db.commit()
        db.refresh(nueva_transaccion)

        return {"estado": 1, "mensaje": "Transacción creada exitosamente."}

    except KeyError as clave_faltante:
        print(f"Error de clave faltante: {clave_faltante}")
        raise HTTPException(status_code=422, detail=f"Falta el campo obligatorio: {clave_faltante}")
    except ValueError as error_conversion:
        print(f"Error de conversión: {error_conversion}")
        raise HTTPException(status_code=422, detail="Error en el formato de los datos enviados.")
    except ValidationError as error_validacion:
        print(f"Errores de validación: {error_validacion.json()}")
        raise HTTPException(status_code=422, detail=error_validacion.errors())
    except Exception as error:
        print(f"Error inesperado: {error}")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno en el servidor.")


@routerTransaccion.post("/procesar_pagos")
def procesar_pagos(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Procesa los pagos pendientes de la tarjeta autenticada (cobros y facturación).
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    if not id_tarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    procesar_pagos_tarjeta(db, id_tarjeta)
    return {"estado": 1, "mensaje": "Pagos procesados correctamente."}


@routerTransaccion.get("/saldo_pendiente")
def saldo_pendiente(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    """
    Calcula el monto total de transacciones fallidas pendientes de recarga en la tarjeta.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    transacciones_fallidas = db.query(Transaccion).filter(
        Transaccion.id_tarjeta == datos_tarjeta.get("id_tarjeta"),
        Transaccion.id_estado == EstadoTransaccion.FALLIDO,
    ).all()

    monto_pendiente = sum([transaccion_fallida.monto for transaccion_fallida in transacciones_fallidas])

    return {
        "estado": 1,
        "mensaje": f"El monto pendiente de recargar es {monto_pendiente:.2f} unidades monetarias.",
        "monto_pendiente": monto_pendiente,
    }

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import and_
from helpers.database import get_db
from helpers.tokens import verificar_token_t
from models.transaccion import Transaccion
from models.servicio import Servicio
from models.estado import Estado
from models.factura import Factura
from models.tarjeta import Tarjeta
from schemas.transaccion_schema import TransaccionCreate
from datetime import datetime
from dateutil.relativedelta import relativedelta

routerTransaccion = APIRouter()

@routerTransaccion.get("/read")
def obtener_facturas(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    if not datos_tarjeta:
        raise HTTPException(status_code=400, detail="Token inválido o expirado.")

    idtarjeta = datos_tarjeta.get("id_tarjeta")
    
    if not idtarjeta:
        raise HTTPException(status_code=400, detail="No se encontró el ID de la tarjeta.")

    # Realizando la consulta con SQLAlchemy
    query = db.query(
        Transaccion.id_transaccion,
        Transaccion.fecha_transaccion,
        Transaccion.hora_transaccion,
        Transaccion.monto,
        Transaccion.frecuencia,
        Transaccion.descripcion,
        Transaccion.id_estado,
        Estado.estado.label('estado'),
        Servicio.nombre.label('nombre')
    ).join(
        Estado, Transaccion.id_estado == Estado.id_estado
    ).join(
        Servicio, Transaccion.id_servicio == Servicio.id_servicio
    ).filter(
            and_(
            Transaccion.id_tarjeta == idtarjeta,
            Transaccion.id_estado != 3
        )
    )

    try:
        # Ejecutar la consulta y obtener los resultados
        result = query.all()
        
        # Si no hay resultados, enviar mensaje adecuado
        if not result:
            return {"estado": 0, "detail": "No se encontraron transacciones."}

        # Formatear los resultados usando KeyedTuple (por nombre)
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
                "nombre": str(row.nombre)
            }
            for row in result
        ]
        
        return {"estado": 1, "dataset": transaccion}

    except Exception as e:
        print(f"Error al obtener las facturas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")



@routerTransaccion.post("/crear")
def crear_transaccion(body: TransaccionCreate, datos_tarjeta=Depends(verificar_token_t),db: Session = Depends(get_db)):
    """
    Crea una nueva transacción en la base de datos.
    """
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    try:
        # Crear instancia del modelo Transaccion
        nueva_transaccion = Transaccion(
            fecha_transaccion=body.fecha_transaccion,
            hora_transaccion=body.hora_transaccion,
            monto=body.monto,
            frecuencia=body.frecuencia,
            descripcion=body.descripcion,
            id_tarjeta=datos_tarjeta.get('id_tarjeta'),
            id_servicio=body.id_servicio,
            id_estado=body.id_estado,
        )

        # Insertar en la base de datos
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
def procesar_pagos(db: Session = Depends(get_db)):
    transacciones = db.query(Transaccion).filter(Transaccion.frecuencia >= 0).all()  # Incluir todas las transacciones con frecuencia >= 0

    for transaccion in transacciones:
        tarjeta = db.query(Tarjeta).filter(Tarjeta.id_tarjeta == transaccion.id_tarjeta).first()

        # Combinamos la fecha y hora de la transacción para crear el datetime de la transacción
        transaccion_datetime = datetime.combine(transaccion.fecha_transaccion, transaccion.hora_transaccion)
        
        # Depuración: Verifica la fecha y hora de la transacción y la fecha actual
        #print(f"Fecha actual: {datetime.now()}, Fecha de transacción: {transaccion_datetime}, Frecuencia: {transaccion.frecuencia}")

        # Verificar si la frecuencia llegó a 0 o si es negativa (para completar la transacción)
        if transaccion.frecuencia == 0:
            transaccion.id_estado = 3  # Estado "Completado"
        # Solo procesar si el balance es suficiente y la fecha de la transacción es válida
        if tarjeta and datetime.now() > transaccion_datetime:
            if tarjeta.balance >= transaccion.monto:
                #print(f"Procesando transacción ID: {transaccion.id_transaccion}")
                
                # Actualizar balance y frecuencia
                tarjeta.balance -= transaccion.monto
                transaccion.frecuencia -= 1
                
                # Verificar si la frecuencia llegó a 0 o si es negativa (para completar la transacción)
                if transaccion.frecuencia <= 0:
                    transaccion.id_estado = 3  # Estado "Completado"
                else:
                    transaccion.id_estado = 2  # Estado "En proceso"
                
                # Crear factura
                factura = Factura(
                    fecha_factura=datetime.now().date(),
                    hora_factura=datetime.now().time(),
                    monto_total=transaccion.monto,
                    id_transaccion=transaccion.id_transaccion
                )
                db.add(factura)
                db.commit()
                db.refresh(factura)

                # Sumar un mes a la fecha de la transacción
                transaccion.fecha_transaccion = transaccion.fecha_transaccion + relativedelta(months=1)
            
            else:
                # Si el balance es insuficiente, actualizar estado a 1 (fallido)
                #print(f"Balance insuficiente para transacción ID: {transaccion.id_transaccion}")
                transaccion.id_estado = 1  # Estado "Fallido" debido a saldo insuficiente

        else:
            # Si la fecha no ha llegado, no hacer nada y no procesar
            #print(f"Transacción ID: {transaccion.id_transaccion} no procesada debido a fecha futura.")
            continue
        
        # Asegurar que el estado se actualiza a 3 cuando la frecuencia es <= 0, incluso si no pasa por la lógica anterior
        if transaccion.frecuencia <= 0 and transaccion.id_estado != 3:
            transaccion.id_estado = 3  # Actualizar a "Completado"

    db.commit()
    #print("Pagos procesados")
    return {"estado": 1, "mensaje": "Pagos procesados correctamente."}

@routerTransaccion.get("/saldo_pendiente")
def saldo_pendiente(datos_tarjeta=Depends(verificar_token_t), db: Session = Depends(get_db)):
    # Obtener todas las tarjetas del usuario
    if not datos_tarjeta:  # Asegúrate de que los datos del token estén presentes
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    # Obtener las transacciones pendientes de esta tarjeta (estado 2)
    transacciones_pendientes = db.query(Transaccion).filter(
        Transaccion.id_tarjeta == datos_tarjeta.get('id_tarjeta'), 
        Transaccion.id_estado == 1  # Estado pendiente
    ).all()

    # Calcular el monto total pendiente de pago
    monto_pendiente = sum([transaccion.monto for transaccion in transacciones_pendientes])

    # Responder con el monto total pendiente
    return {
        "estado": 1,
        "mensaje": f"El monto pendiente de recargar es {monto_pendiente:.2f} unidades monetarias.",
        "monto_pendiente": monto_pendiente
    }


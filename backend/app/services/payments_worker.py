from datetime import datetime

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.factura import Factura
from app.models.transaccion import Transaccion
from app.services.wallet import debitar_saldo


def procesar_pagos_tarjeta(db: Session, id_tarjeta: int) -> None:
    transacciones = db.query(Transaccion).filter(
        Transaccion.id_tarjeta == id_tarjeta,
        Transaccion.frecuencia >= 0,
    ).all()

    for transaccion in transacciones:
        transaccion_datetime = datetime.combine(
            transaccion.fecha_transaccion, transaccion.hora_transaccion
        )

        if transaccion.frecuencia == 0:
            transaccion.id_estado = 3
        if datetime.now() > transaccion_datetime:
            try:
                debitar_saldo(db, transaccion.id_tarjeta, transaccion.monto, referencia=str(transaccion.id_transaccion))
                transaccion.frecuencia -= 1

                if transaccion.frecuencia <= 0:
                    transaccion.id_estado = 3
                else:
                    transaccion.id_estado = 2

                factura = Factura(
                    fecha_factura=datetime.now().date(),
                    hora_factura=datetime.now().time(),
                    monto_total=transaccion.monto,
                    id_transaccion=transaccion.id_transaccion,
                )
                db.add(factura)
                db.commit()
                db.refresh(factura)

                transaccion.fecha_transaccion = transaccion.fecha_transaccion + relativedelta(
                    months=1
                )

            except HTTPException as e:
                if e.status_code == 400 and e.detail == "Saldo insuficiente":
                    transaccion.id_estado = 1
                elif e.status_code == 404:
                    continue
                else:
                    raise

        else:
            continue

        if transaccion.frecuencia <= 0 and transaccion.id_estado != 3:
            transaccion.id_estado = 3

    db.commit()


def procesar_pagos_todas_tarjetas(db: Session) -> int:
    id_tarjetas = (
        db.query(Transaccion.id_tarjeta)
        .filter(Transaccion.frecuencia >= 0)
        .distinct()
        .all()
    )

    for (id_tarjeta,) in id_tarjetas:
        procesar_pagos_tarjeta(db, id_tarjeta)

    return len(id_tarjetas)

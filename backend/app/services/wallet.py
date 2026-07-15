from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.historial import Historial
from app.models.tarjeta import Tarjeta


def recargar_saldo(db: Session, id_tarjeta: int, monto) -> Historial:
    monto_decimal = Decimal(str(monto))
    if monto_decimal <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a 0")

    tarjeta = (
        db.query(Tarjeta)
        .filter(Tarjeta.id_tarjeta == id_tarjeta)
        .with_for_update()
        .first()
    )

    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    tarjeta.balance = tarjeta.balance + monto_decimal
    tarjeta.fecha_actualizacion = datetime.now().date()

    now = datetime.now()
    historial = Historial(
        monto_agregado=monto_decimal,
        fecha_historial=now.date(),
        hora_historial=now.time(),
        id_tarjeta=id_tarjeta,
    )
    db.add(historial)
    db.commit()
    db.refresh(historial)
    return historial


def debitar_saldo(db: Session, id_tarjeta: int, monto) -> Tarjeta:
    monto_decimal = Decimal(str(monto))

    tarjeta = (
        db.query(Tarjeta)
        .filter(Tarjeta.id_tarjeta == id_tarjeta)
        .with_for_update()
        .first()
    )

    if not tarjeta:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    if tarjeta.balance < monto_decimal:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    tarjeta.balance = tarjeta.balance - monto_decimal
    tarjeta.fecha_actualizacion = datetime.now().date()
    db.flush()
    return tarjeta

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.historial import Historial
from app.models.movimiento import Movimiento
from app.models.tarjeta import Tarjeta


def _registrar_movimiento(
    db: Session,
    id_tarjeta: int,
    tipo: str,
    monto: Decimal,
    saldo_anterior: Decimal,
    saldo_nuevo: Decimal,
    referencia: str | None = None,
) -> Movimiento:
    movimiento = Movimiento(
        id_tarjeta=id_tarjeta,
        tipo=tipo,
        monto=monto,
        saldo_anterior=saldo_anterior,
        saldo_nuevo=saldo_nuevo,
        referencia=referencia,
        creado_en=datetime.now(),
    )
    db.add(movimiento)
    return movimiento


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

    saldo_anterior = tarjeta.balance
    tarjeta.balance = saldo_anterior + monto_decimal
    tarjeta.fecha_actualizacion = datetime.now().date()

    now = datetime.now()
    historial = Historial(
        monto_agregado=monto_decimal,
        fecha_historial=now.date(),
        hora_historial=now.time(),
        id_tarjeta=id_tarjeta,
    )
    db.add(historial)
    db.flush()

    _registrar_movimiento(
        db,
        id_tarjeta,
        "recarga",
        monto_decimal,
        saldo_anterior,
        tarjeta.balance,
        referencia=str(historial.id_historial),
    )
    db.commit()
    db.refresh(historial)
    return historial


def debitar_saldo(
    db: Session,
    id_tarjeta: int,
    monto,
    referencia: str | None = None,
) -> Tarjeta:
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

    saldo_anterior = tarjeta.balance
    tarjeta.balance = saldo_anterior - monto_decimal
    tarjeta.fecha_actualizacion = datetime.now().date()

    _registrar_movimiento(
        db,
        id_tarjeta,
        "debito",
        monto_decimal,
        saldo_anterior,
        tarjeta.balance,
        referencia=referencia,
    )
    db.flush()
    return tarjeta

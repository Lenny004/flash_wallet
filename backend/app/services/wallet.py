"""Operaciones de saldo: recargas, débitos y registro de movimientos."""

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
    """Persiste un movimiento de wallet sin hacer commit.

    Args:
        db: Sesión SQLAlchemy activa.
        id_tarjeta: Tarjeta afectada.
        tipo: Tipo de movimiento (``recarga``, ``debito``, etc.).
        monto: Importe del movimiento.
        saldo_anterior: Balance antes de la operación.
        saldo_nuevo: Balance después de la operación.
        referencia: Identificador externo opcional (p. ej. id de historial).

    Returns:
        Instancia de ``Movimiento`` añadida a la sesión.
    """
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
    """Acredita saldo a una tarjeta y registra historial + movimiento.

    Args:
        db: Sesión SQLAlchemy.
        id_tarjeta: Tarjeta a recargar.
        monto: Importe positivo a acreditar.

    Returns:
        Registro de ``Historial`` creado.

    Raises:
        HTTPException: 400 si el monto no es positivo; 404 si no existe la tarjeta.
    """
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
    tarjeta.fecha_actualizacion = datetime.now()

    ahora = datetime.now()
    historial = Historial(
        monto_agregado=monto_decimal,
        fecha_historial=ahora.date(),
        hora_historial=ahora.time(),
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
    """Debita saldo de una tarjeta con bloqueo pesimista (``FOR UPDATE``).

    Args:
        db: Sesión SQLAlchemy.
        id_tarjeta: Tarjeta a debitar.
        monto: Importe a descontar.
        referencia: Identificador externo opcional (p. ej. id de transacción).

    Returns:
        Tarjeta actualizada (sin commit; el llamador decide cuándo confirmar).

    Raises:
        HTTPException: 400 si saldo insuficiente; 404 si no existe la tarjeta.
    """
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
    tarjeta.fecha_actualizacion = datetime.now()

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

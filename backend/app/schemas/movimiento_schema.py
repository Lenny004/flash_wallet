from datetime import datetime

from pydantic import BaseModel, Field


class TablaMovimiento(BaseModel):
    """Movimiento de saldo de una tarjeta digital."""

    id_movimiento: int = Field(..., ge=1)
    id_tarjeta: int = Field(..., ge=1)
    tipo: str
    monto: float = Field(..., gt=0)
    saldo_anterior: float = Field(..., ge=0)
    saldo_nuevo: float = Field(..., ge=0)
    referencia: str | None = None
    creado_en: datetime

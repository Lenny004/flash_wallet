from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class TransaccionCreate(BaseModel):
    """Datos para crear una transacción de pago."""

    fecha_transaccion: date
    hora_transaccion: time
    monto: float = Field(..., gt=0)
    frecuencia: int = Field(..., ge=1)
    descripcion: str = Field(..., max_length=40)
    id_tarjeta: Optional[int] = Field(default=None, ge=1)
    id_servicio: int = Field(..., ge=1)
    id_estado: int = Field(..., ge=1)

    model_config = {"from_attributes": True}


class TransaccionDesdeIntent(TransaccionCreate):
    """Transacción creada a partir de un payment intent firmado (QR)."""

    exp: int = Field(..., ge=1)
    sig: str = Field(..., min_length=64, max_length=64)

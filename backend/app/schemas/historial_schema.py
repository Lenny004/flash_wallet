from datetime import date, time

from pydantic import BaseModel, Field


class TablaHistorial(BaseModel):
    """Registro de depósito en el historial de una tarjeta."""

    id_historial: int = Field(..., ge=1)
    monto_agregado: float = Field(..., gt=0)
    fecha_historial: date
    hora_historial: time
    id_tarjeta: int = Field(..., ge=1)


class BuscarHistorialRequest(BaseModel):
    """Criterio de búsqueda o monto de recarga en historial."""

    monto_agregado: float = Field(..., gt=0)


class EliminarHistorial(BaseModel):
    """Identificador de registro de historial a eliminar."""

    id_historial: int = Field(..., ge=1)

    model_config = {"from_attributes": True}

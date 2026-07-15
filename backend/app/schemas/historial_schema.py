from datetime import date, time

from pydantic import BaseModel, Field


class TablaHistorial(BaseModel):
    id_historial: int = Field(..., ge=1)
    monto_agregado: float = Field(..., gt=0)
    fecha_historial: date
    hora_historial: time
    id_tarjeta: int = Field(..., ge=1)


class BuscarHistorialRequest(BaseModel):
    monto_agregado: float = Field(..., gt=0)


class EliminarHistorial(BaseModel):
    id_historial: int = Field(..., ge=1)

    model_config = {"from_attributes": True}

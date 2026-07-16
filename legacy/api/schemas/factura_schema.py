from pydantic import BaseModel, Field
from datetime import date, time

class FacturaResponse(BaseModel):
    id_factura: int = Field(..., ge=1)
    monto_total: float = Field(..., gt=0)
    fecha_factura: date
    hora_factura: time

class CrearFacturaRequest(BaseModel):
    fecha_factura: date
    hora_factura: time
    monto_total: float = Field(..., gt=0)

class BuscarFactura(BaseModel):
    nombre: str = Field(..., max_length=30)

class EliminarFactura(BaseModel):
    id_factura: int = Field(..., ge=1)

    model_config = {"from_attributes": True}

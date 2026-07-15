from datetime import date, time

from pydantic import BaseModel, Field


class FacturaResponse(BaseModel):
    """Factura emitida tras un pago completado."""

    id_factura: int = Field(..., ge=1)
    monto_total: float = Field(..., gt=0)
    fecha_factura: date
    hora_factura: time


class CrearFacturaRequest(BaseModel):
    """Datos para registrar una nueva factura."""

    fecha_factura: date
    hora_factura: time
    monto_total: float = Field(..., gt=0)


class BuscarFactura(BaseModel):
    """Criterio de búsqueda de factura por nombre de servicio."""

    nombre: str = Field(..., max_length=30)


class EliminarFactura(BaseModel):
    """Identificador de factura a eliminar."""

    id_factura: int = Field(..., ge=1)

    model_config = {"from_attributes": True}

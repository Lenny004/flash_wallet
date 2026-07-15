from pydantic import BaseModel, Field


class ServicioOut(BaseModel):
    """Servicio expuesto en listados de la API."""

    id: int = Field(..., ge=1)
    nombre: str
    img_servicio: str


class ServiciosListResponse(BaseModel):
    """Listado de servicios con estado de operación."""

    estado: int
    dataset: list[ServicioOut]

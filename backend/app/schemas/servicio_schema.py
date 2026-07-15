from pydantic import BaseModel, Field


class ServicioOut(BaseModel):
    id: int = Field(..., ge=1)
    nombre: str
    img_servicio: str


class ServiciosListResponse(BaseModel):
    estado: int
    dataset: list[ServicioOut]

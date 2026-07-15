from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class EstadoMensaje(BaseModel):
    estado: int
    mensaje: str | None = None

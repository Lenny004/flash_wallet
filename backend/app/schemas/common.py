from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: Literal["ok", "error"]


class EstadoMensaje(BaseModel):
    estado: int
    mensaje: str | None = None

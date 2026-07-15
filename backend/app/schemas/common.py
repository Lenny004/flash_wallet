from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud de la API y la base de datos."""

    status: str
    database: Literal["ok", "error"]


class EstadoMensaje(BaseModel):
    """Respuesta genérica con código de estado y mensaje opcional."""

    estado: int
    mensaje: str | None = None

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    """Datos de registro de un nuevo usuario."""

    nombres: str = Field(..., max_length=50)
    apellidos: str = Field(..., max_length=50)
    direccion: str = Field(..., max_length=150)
    telefono: str = Field(..., max_length=15)
    email: EmailStr
    usuario: str = Field(..., max_length=50)
    contra: str = Field(..., min_length=6)
    img_usuario: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """Credenciales para inicio de sesión."""

    usuario: str = Field(..., max_length=50)
    contra: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    """Refresh token para renovar o revocar la sesión."""

    refresh_token: str


class UsuarioUpdate(BaseModel):
    """Campos editables del perfil de usuario."""

    direccion: str = Field(..., max_length=150)
    telefono: str = Field(..., max_length=15)
    email: EmailStr

    model_config = {"from_attributes": True}


class HayUsuariosResponse(BaseModel):
    """Indica si ya existen usuarios registrados (primer uso)."""

    estado: int
    hay_usuarios: bool
    exception: str | None = None

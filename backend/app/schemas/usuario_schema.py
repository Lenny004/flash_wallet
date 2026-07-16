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
    """Credenciales para inicio de sesión (usuario o email + contraseña)."""

    usuario: str = Field(..., max_length=50, description="Nombre de usuario o correo electrónico")
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


class ForgotPasswordRequest(BaseModel):
    """Solicitud de recuperación de contraseña por correo."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Restablecimiento de contraseña con código de verificación."""

    email: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)
    nueva_contra: str = Field(..., min_length=6, max_length=50)


class HayUsuariosResponse(BaseModel):
    """Indica si ya existen usuarios registrados (primer uso)."""

    estado: int
    hay_usuarios: bool
    exception: str | None = None

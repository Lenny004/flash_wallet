from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UsuarioCreate(BaseModel):
    nombres: str = Field(..., max_length=50)
    apellidos: str = Field(..., max_length=50)
    direccion: str = Field(..., max_length=150)
    telefono: str = Field(..., max_length=15)
    email: EmailStr
    usuario: str = Field(..., max_length=50)
    contra: str = Field(..., min_length=6)
    img_usuario: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    usuario: str = Field(..., max_length=50)
    contra: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    direccion: str = Field(..., max_length=150)
    telefono: str = Field(..., max_length=15)
    email: EmailStr

    model_config = {"from_attributes": True}

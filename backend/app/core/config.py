"""Configuración de la aplicación cargada desde variables de entorno."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py → raíz del proyecto (Flash/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Parámetros de entorno y valores por defecto del backend."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Base de datos ---
    database_url: str = "mysql+pymysql://root@localhost/dbflash"

    # --- Auth JWT ---
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7

    # --- CORS y API interna ---
    cors_origins: list[str] = ["http://localhost", "http://127.0.0.1"]
    internal_api_token: str = "dev-internal-token"

    # --- Workers e intents QR ---
    payments_poll_seconds: int = 30
    qr_intent_ttl_seconds: int = 300

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Convierte una cadena separada por comas en lista de orígenes CORS.

        Args:
            value: Lista ya parseada o cadena ``"http://a,http://b"``.

        Returns:
            Lista de orígenes sin espacios en blanco.
        """
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia singleton de configuración (cacheada)."""
    return Settings()


settings = get_settings()

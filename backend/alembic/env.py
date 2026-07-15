import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# backend/ en PYTHONPATH para importar app.*
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

try:
    from app.core.config import settings
    from app.db.base import Base
    import app.models  # noqa: F401 — registra tablas en Base.metadata
except ImportError as exc:
    raise SystemExit(
        "\n[alembic] No se pudo importar el paquete `app`.\n"
        "  - Ejecuta Alembic desde el directorio `backend/`.\n"
        "  - Verifica que existan `app/core/config.py` y `app/db/base.py`.\n"
        f"  - Detalle: {exc}\n"
    ) from exc

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline' (solo SQL, sin engine)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online' (con engine de SQLAlchemy)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

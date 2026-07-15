# Backend Flash

API FastAPI con SQLAlchemy y Alembic.

## Inicio rápido

```bash
# Desde backend/
pip install -r ../requirements.txt
```

Copia `.env.example` a `.env` en la raíz del proyecto (`Flash/.env`) y completa los valores.

```bash
uvicorn app.main:app --reload
```

## Migraciones (Alembic)

Ejecuta los comandos desde `backend/`:

```bash
alembic revision --autogenerate -m "inicial"
alembic upgrade head
```

`sqlalchemy.url` en `alembic.ini` es un placeholder; `alembic/env.py` lo sobrescribe con `settings.database_url` de `app.core.config`.

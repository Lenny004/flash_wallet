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

### Bases de datos existentes

Si ya tienes `dbflash` cargada (XAMPP o volumen Docker) y falta la tabla `tbmovimiento`, levanta MySQL y aplica la migración:

```bash
docker compose up db
cd backend && alembic upgrade head
```

## Variables de entorno

Verifica que `SECRET_KEY` y `DATABASE_URL` estén definidos en `Flash/.env`:

```bash
python scripts/check_env.py
```

# Stack tecnológico

## Stack actual (detectado)

| Capa | Tecnología |
|------|------------|
| Framework web | FastAPI |
| Servidor ASGI | Uvicorn |
| ORM | SQLAlchemy |
| Driver DB | pymysql |
| Base de datos | MySQL 8 (vía XAMPP) |
| Validación | Pydantic v1 (`orm_mode`) |
| Auth | PyJWT (HS256) |
| Contraseñas | passlib + bcrypt |
| QR | pyzbar + Pillow |
| Fechas | python-dateutil |
| Frontend | HTML + CSS + JavaScript vanilla |
| Alertas UI | SweetAlert2 |
| Fuente | Inter |

No existe `requirements.txt` ni gestión de dependencias; el stack se infiere de los imports.

## Stack objetivo (2025-2026)

| Capa | Recomendación | Justificación |
|------|---------------|---------------|
| API | FastAPI (mantener) | Ya implementado; async nativo, OpenAPI automático |
| Validación | Pydantic v2 + `response_model` | Tipado estricto entrada/salida, mejor rendimiento |
| ORM | SQLAlchemy 2.x | API moderna; opción async futura |
| Migraciones | Alembic | Versionar el esquema; elimina `dbflash.sql` manual |
| Base de datos | MySQL 8 en Docker | Continuidad con el esquema actual, reproducible |
| Auth | JWT access (15 min) + refresh (7 días) | Sesiones cortas + renovación; secretos en `.env` |
| Config | Pydantic Settings | Centraliza env; sin hardcode |
| Frontend (F1-F2) | Vite + TypeScript vanilla | Build reproducible sin reescribir en React |
| Frontend (F5) | React 19 + TanStack Query | Solo para páginas críticas cuando el core esté sólido |
| UI | CSS actual componentizado | Preservar identidad visual existente |
| QR | pyzbar/opencv backend + html5-qrcode browser | Escaneo en navegador + validación firmada |
| Tiempo real | WebSocket/SSE (FastAPI) | Confirmación de pago sin polling |
| Contenedores | Docker Compose (`api`, `db`, `frontend`) | Un solo `compose up` para todo el equipo |
| Formato/lint | ruff | Rápido, reemplaza black + isort + flake8 |
| Tests | pytest + httpx | Cobertura de auth, transacción, QR |
| CI | GitHub Actions | Lint + tests + build en cada PR |
| Observabilidad | logging estructurado + `/health` | Diagnóstico y healthchecks de Docker |

## Stack mínimo viable profesional

Lo más pequeño que ya se siente profesional, sin reescrituras grandes:

```
FastAPI + SQLAlchemy + Alembic + MySQL 8 (Docker)
+ Vite (TS vanilla) + GitHub Actions + pytest + ruff
```

## Justificación de decisiones clave

- **Mantener FastAPI:** el backend ya está bien encaminado (routers, schemas, JWT). Migrar
  a Flask/Django sería retroceder.
- **MySQL antes que PostgreSQL:** el esquema y los datos ya existen en MySQL; migrar el motor
  ahora añade riesgo sin beneficio inmediato. PostgreSQL se evalúa en Fase 5 si el despliegue
  cloud o las restricciones lo justifican.
- **Vite con TS vanilla antes que React:** permite eliminar las URLs hardcodeadas y tener build
  reproducible sin reescribir toda la UI. React llega solo cuando aporte valor real.
- **Alembic:** versionar el esquema es requisito para trabajo en equipo y despliegues repetibles.

## Dependencias a fijar (backend)

Al ejecutar la Fase 1 se creará un `requirements.txt`/`pyproject.toml` con versiones fijadas de:

```
fastapi
uvicorn[standard]
sqlalchemy
pymysql
pyjwt
passlib[bcrypt]
pydantic
pydantic-settings
email-validator
python-dateutil
pyzbar
Pillow
alembic
pytest
httpx
ruff
```

# Auditoría de readiness para despliegue — Flash Wallet v0.2.0

**Fecha:** 2026-07-15 (revisión post-fixes)  
**Alcance:** solo lectura del repositorio + verificación local parcial (`npm run build` OK; Python/Docker daemon no disponibles en el entorno de auditoría).  
**Criterio:** despliegue a **staging** con `docker compose` en un solo host (réplica única), sin hardening de producción completo.

---

## Resumen ejecutivo

El proyecto tiene base sólida para **staging monolítico** (compose de 3 servicios, healthchecks, CI con pytest y build de frontend, Pydantic v2, auth en la mayoría de endpoints). Los fixes recientes (Dockerfile con `libzbar0` + Alembic, CVC enmascarado en `readOne`, migración completa de páginas Vite a TypeScript, docstrings en `core/` y `routes/`) eliminan los bloqueantes técnicos de código. **Quedan solo pasos manuales de configuración** antes del primer `compose up`.

| Área | Estado global |
|------|---------------|
| Backend FastAPI | PARCIAL |
| Frontend Vite | LISTO |
| Docker / Compose | PARCIAL |
| DB / Alembic | PARCIAL |
| CI | PARCIAL |
| Seguridad | PARCIAL |
| Tests | PARCIAL |

---

## 1. Checklist por módulo

Leyenda: **LISTO** = desplegable sin cambios; **PARCIAL** = funciona con pasos manuales o riesgos conocidos; **BLOQUEANTE** = falla o es inaceptable sin corrección previa.

### Backend (FastAPI)

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| App arranca con uvicorn | PARCIAL | `backend/Dockerfile` OK; requiere `SECRET_KEY` en `.env` (sin default en `config.py`) |
| Healthcheck `/health` | LISTO | DB probe en `main.py`; compose usa healthcheck HTTP |
| CORS configurable | PARCIAL | `settings.cors_origins` desde env; default solo `localhost` / `127.0.0.1` |
| Pydantic v2 + Settings | LISTO | `requirements.txt` + `BaseSettings` en `config.py` |
| Worker de pagos en lifespan | PARCIAL | `_payments_poll_loop()` en cada proceso API → duplicación si hay >1 réplica |
| Endpoint interno de pagos | PARCIAL | `/api/internal/procesar_pagos` protegido por `X-Internal-Token`; default `dev-internal-token` |
| Decode QR (pyzbar) | LISTO | `backend/Dockerfile` instala `libzbar0` antes de `pip install` |
| Migraciones en imagen | LISTO | Dockerfile copia `backend/alembic/` y `backend/alembic.ini` |
| Documentación `core/` y `routes/` | LISTO | Docstrings de módulo en `core/*.py`; endpoints con `Auth:` en docstrings de `routes/*.py` |
| Registro expone PAN/CVC | PARCIAL | `POST /api/usuarios/` devuelve `pan` y `cvc` **una vez** (tarjeta_digital); documentado en código |
| GET tarjeta expone CVC | LISTO | `GET /api/tarjeta/readOne` devuelve `cvc: "***"`; PAN visible para UI de tarjeta digital |
| Blacklist refresh en memoria | PARCIAL | `token_blacklist.py` — se pierde al reiniciar; no compartida entre réplicas |
| Rate limit en memoria | PARCIAL | `rate_limit.py` — mismo problema multi-réplica |
| Legacy `api/` coexistiendo | PARCIAL | Carpeta legacy aún presente; no entra en imagen Docker actual |

### Frontend (Vite)

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| `npm run build` | LISTO | Verificado localmente (tsc + vite build sin errores) |
| Multi-page build (9 páginas TS) | LISTO | `vite.config.ts`: login, registro, dashboard, pago, recarga, escanear_servicio, perfil, historial_pago, tarjeta_digital + `src/pages/*.ts` |
| API base URL | LISTO (Docker) | `client.ts`: `VITE_API_URL ?? ''` → rutas relativas `/api/...` vía Nginx |
| API base URL (build con URL absoluta) | PARCIAL | Si se bakea `VITE_API_URL=http://localhost:8000` en build, rompe en staging |
| Proxy dev Vite | LISTO | Solo afecta `npm run dev`, no producción |
| Código legacy (`controllers/`) | PARCIAL | Copiado a `public/`; convive con TS nuevo |

### Docker

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| `docker-compose.yml` 3 servicios | LISTO | `db`, `api`, `frontend` con `depends_on` + health |
| Host MySQL en API | LISTO | `DATABASE_URL` en compose usa host `db` (no `localhost`) |
| `env_file: .env` obligatorio | PARCIAL | Sin `.env` real, `api` no arranca (`SECRET_KEY` requerida) |
| Puerto MySQL expuesto | PARCIAL | `3306:3306` — aceptable en dev/staging interno; cerrar en prod |
| Healthcheck API usa `python` | LISTO | Imagen `python:3.12-slim` incluye `python` en PATH |
| Build API con libzbar + Alembic | LISTO | `libzbar0` + `COPY backend/alembic` en `backend/Dockerfile` |
| `docker-compose.override.yml` | PARCIAL | Documentado en `docs/DOCKER.md` pero **no existe** en el repo |
| CI build Docker | PARCIAL | Jobs `docker-api` y `docker-frontend` con `continue-on-error: true` |
| Daemon Docker en auditoría | PARCIAL | CLI instalada; daemon no corriendo — no se validó `compose up` end-to-end |

### DB / Alembic

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| Esquema semilla `dbflash.sql` | LISTO | Incluye `tbmovimiento` (actualizado) |
| Init DB en primer arranque | LISTO | Volumen + `/docker-entrypoint-initdb.d/001_schema.sql` |
| Volumen existente sin re-init | PARCIAL | Cambios en SQL no se aplican solos; hace falta migración manual |
| Alembic configurado | LISTO | `backend/alembic.ini` + `env.py` lee `settings.database_url` |
| Migración `001_tbmovimiento` | PARCIAL | Solo útil si la DB **no** tiene `tbmovimiento`; redundante en DB nueva con SQL actual |
| Alembic en contenedor API | LISTO | Copiado en Dockerfile; ejecutable con `docker compose exec api alembic upgrade head` |
| `alembic upgrade` en entrypoint | BLOQUEANTE (ops) | No hay script de arranque que migre automáticamente; paso manual si DB antigua |

### CI (`.github/workflows/ci.yml`)

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| Pytest en push/PR | LISTO | Job `lint-and-test` con `SECRET_KEY` de CI |
| Frontend build en CI | LISTO | `npm ci` + `npm run build` |
| Ruff lint | PARCIAL | `continue-on-error: true` — deuda de estilo no bloquea merge |
| Docker build en CI | PARCIAL | `continue-on-error: true` — imagen rota no falla el pipeline |
| Tests con MySQL real | BLOQUEANTE (cobertura) | Solo smoke tests sin DB; health puede reportar `degraded` |
| `docker compose up` en CI | BLOQUEANTE (cobertura) | No hay test de integración compose |
| Alembic en CI | BLOQUEANTE (cobertura) | No se ejecuta `alembic upgrade head` |

### Seguridad

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| `SECRET_KEY` fuera del código | LISTO | Settings obligatorio; `.env` en `.gitignore` |
| `SECRET_KEY` con valor real en deploy | **BLOQUEANTE (ops)** | `.env.example` tiene placeholder `genera_una_clave_nueva`; hay que generarlo antes del deploy |
| `INTERNAL_API_TOKEN` fuerte | PARCIAL | Default `dev-internal-token` en `config.py` y `.env.example` |
| CORS restrictivo | PARCIAL | Ya no es `*`; hay que añadir URL exacta de staging |
| PAN/CVC en respuestas API | PARCIAL | Registro expone CVC una vez; `readOne` enmascara CVC (`"***"`); PAN visible en dashboard |
| PAN/CVC en BD en claro | PARCIAL | Columnas `pan`, `cvc` sin cifrado |
| JWT sin datos sensibles | LISTO | Tokens llevan ids, no PAN/CVC (corregido respecto a legacy) |
| Auth en endpoints mutables | LISTO | Tests confirman 401 sin token en rutas críticas |
| Blacklist / rate limit distribuidos | PARCIAL | Solo memoria de proceso |
| HTTPS / TLS | BLOQUEANTE (prod) | Compose sirve HTTP plano en 8080/8000 |
| Tokens en localStorage | PARCIAL | Riesgo XSS documentado en `SEGURIDAD.md` |

### Tests

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| Suite pytest | PARCIAL | ~22 tests (smoke, auth guards, QR intent, rate limit) |
| Cobertura integración DB | BLOQUEANTE | No hay fixtures MySQL ni tests E2E |
| Cobertura registro/PAN | PARCIAL | CVC enmascarado en `readOne`; registro aún expone CVC una vez |
| Ejecución local Windows | PARCIAL | `python`/`py`/`pytest` no en PATH en entorno auditado; usar `python -m pytest` con venv |
| CI como red de seguridad | PARCIAL | Pasa en GitHub; no valida compose ni QR en Docker |

---

## 2. Errores probables en producción / staging

### Críticos (caída o funcionalidad rota)

| Error | Síntoma | Causa raíz | Mitigación |
|-------|---------|------------|------------|
| API no arranca | Contenedor `flash_api` en restart loop | Falta `.env` o `SECRET_KEY` vacía/placeholder | Generar clave (`secrets.token_hex(32)`), crear `.env` antes de `compose up` |
| `ValidationError` al importar Settings | Crash al inicio | Pydantic v2 exige `secret_key: str` sin default | Igual que arriba |
| Decode QR 500 / ValueError | Escaneo falla siempre en Docker | ~~`pyzbar` requiere `libzbar0` no instalada en imagen slim~~ | **Resuelto:** `libzbar0` en Dockerfile |
| Frontend no llega a API (CORS) | Browser bloquea `fetch` | `CORS_ORIGINS` sin URL de staging (solo localhost) | Añadir `https://staging.tudominio.com` o `http://host:8080` |
| DB connection refused | Health `degraded`, 500 en rutas | `DATABASE_URL` con `@localhost` dentro del contenedor API | En compose, confiar en override `environment.DATABASE_URL` con host `db`; no poner localhost en `.env` si se usa compose |
| `tbmovimiento` no existe | Error al recargar/debitar | Volumen Docker antiguo creado antes de SQL con ledger | `docker compose exec api alembic upgrade head` (o desde host con `cd backend`) |
| Pagos duplicados | Doble débito / facturas repetidas | Varias réplicas API, cada una con `_payments_poll_loop` | Una sola réplica API en staging, o extraer worker a servicio único |

### Seguridad / datos

| Error | Síntoma | Causa raíz | Mitigación |
|-------|---------|------------|------------|
| PAN/CVC en registro | Respuesta JSON visible en DevTools | `POST /api/usuarios/` devuelve `tarjeta.cvc` **una vez** al crear cuenta | Aceptable para demo/staging interno; CVC no se repite en `readOne` |
| PAN en dashboard | `GET /api/tarjeta/readOne` | PAN completo para UI de tarjeta digital; CVC enmascarado (`"***"`) | Comportamiento esperado en staging |
| Logout inefectivo tras restart | Refresh sigue válido | Blacklist en memoria | Aceptable en staging interno; Redis/DB para prod |
| Rate limit bypass | Fuerza bruta distribuida | Limiter por proceso | Proxy/WAF o Redis |
| Token interno adivinable | Llamadas a `/api/internal/procesar_pagos` | Default `dev-internal-token` | Rotar `INTERNAL_API_TOKEN` en `.env` antes del deploy |

### Configuración / entorno

| Error | Síntoma | Causa raíz | Mitigación |
|-------|---------|------------|------------|
| Frontend llama a `localhost:8000` | 404/CORS en staging | Build con `VITE_API_URL` absoluta incorrecta | Dejar `VITE_API_URL` vacío en build Docker (rutas relativas + Nginx) |
| `python` no encontrado (local) | Scripts/README fallan en Windows | Python no en PATH; alias Store | Usar venv + `python -m uvicorn`, documentar `py` launcher |
| Healthcheck API falla | Contenedor unhealthy | API tarda en conectar a DB | Ya hay `depends_on: db healthy`; revisar credenciales MySQL |
| Puerto 3306 conflicto | `db` no levanta | XAMPP MySQL ya en 3306 | Cambiar mapping o parar XAMPP |

### Pydantic v2 (ya mitigado en código)

| Riesgo | Estado |
|--------|--------|
| `field_validator` para `cors_origins` CSV | OK en `config.py` |
| `EmailStr`, `Field`, `model_config` en schemas | OK |
| Settings `extra="ignore"` | OK — variables Docker/MySQL extra no rompen |

---

## 3. Archivos y configuraciones que DEBEN existir antes del deploy

### Obligatorios (bloquean arranque)

| Archivo / config | Ubicación | Requisito |
|------------------|-----------|-----------|
| `.env` | Raíz `Flash/.env` | Copiado de `.env.example`, **nunca** commiteado |
| `SECRET_KEY` | `.env` | Valor aleatorio ≥ 32 bytes hex; no el placeholder |
| `MYSQL_ROOT_PASSWORD` | `.env` | Coincide con compose y `DATABASE_URL` |
| `MYSQL_DATABASE` | `.env` | Típicamente `dbflash` |
| `docker-compose.yml` | Raíz | Presente |
| `dbflash.sql` | Raíz | Montado en init de MySQL |
| `backend/Dockerfile` | Repo | Presente (libzbar0 + Alembic) |
| `frontend/Dockerfile` | Repo | Presente |
| `frontend/nginx.conf` | Repo | Proxy `/api` → `api:8000` |
| `requirements.txt` | Raíz | Dependencias Python |
| `frontend/package-lock.json` | Repo | Requerido por `npm ci` en Docker |

### Fuertemente recomendados (staging)

| Archivo / config | Notas |
|------------------|-------|
| `CORS_ORIGINS` en `.env` | Incluir origen exacto del frontend staging |
| `INTERNAL_API_TOKEN` en `.env` | Valor único, no `dev-internal-token` |
| `JWT_EXPIRE_MINUTES` / `JWT_REFRESH_EXPIRE_DAYS` | Ajustar política de sesión |
| `VITE_API_URL=` vacío | En build Docker (default actual) |
| `LICENSE` | Existe en repo |
| Volúmenes Docker nombrados | `db_data` se crea automáticamente |

### Para migraciones manuales (si aplica)

| Archivo | Cuándo |
|---------|--------|
| `backend/alembic.ini` | `alembic upgrade head` desde host **o** contenedor API |
| `backend/alembic/env.py` | Lee `DATABASE_URL` del `.env` |
| `backend/alembic/versions/001_tbmovimiento.py` | DB sin tabla `tbmovimiento` (volumen antiguo) |

### No deben existir en el artefacto de deploy

| Elemento | Motivo |
|----------|--------|
| `.env` en git | Secretos |
| `SECRET_KEY=genera_una_clave_nueva` | Placeholder inseguro |
| `frontend/dist/` versionado | Generado en build (en `.gitignore`) |

---

## 4. Comandos de verificación

> Ejecutar desde la raíz del proyecto (`Flash/`) salvo donde se indique. En Windows PowerShell, usar `;` en lugar de `&&`.

### Pre-flight (secretos y env)

```powershell
# Crear .env si no existe
Copy-Item .env.example .env
# Editar .env: SECRET_KEY, CORS_ORIGINS, INTERNAL_API_TOKEN, contraseñas MySQL

# Verificar variables mínimas (requiere Python en PATH o venv activo)
cd backend
python scripts/check_env.py
cd ..
```

### Backend — tests

```powershell
cd backend
$env:SECRET_KEY = "clave-de-prueba-minimo-32-caracteres!!"
$env:DATABASE_URL = "mysql+pymysql://root:flash_dev@127.0.0.1:3306/dbflash"
python -m pytest -q
cd ..
```

### Frontend — build

```powershell
cd frontend
npm ci
npm run build
cd ..
```

### Alembic (DB existente sin tbmovimiento)

```powershell
# Opción A: dentro del contenedor API (Alembic ya copiado en imagen)
docker compose up -d db api
docker compose exec api alembic current
docker compose exec api alembic upgrade head

# Opción B: desde host con Python
cd backend
$env:DATABASE_URL = "mysql+pymysql://root:flash_dev@127.0.0.1:3306/dbflash"
alembic current
alembic upgrade head
cd ..
```

### Docker Compose — build y arranque

```powershell
docker compose build
docker compose up -d
docker compose ps
docker compose logs api --tail 50
docker compose logs db --tail 20
```

### Health checks

```powershell
# API directa
curl http://localhost:8000/health

# Vía Nginx frontend
curl http://localhost:8080/health

# Esperado (DB ok): {"status":"ok","database":"ok"}
```

### Smoke funcional post-deploy

```powershell
# ¿Hay usuarios? (público)
curl http://localhost:8080/api/usuarios/

# Docs API
curl -o NUL -w "%{http_code}" http://localhost:8000/docs
```

### Verificación QR en Docker (detecta libzbar)

```powershell
docker compose exec api python -c "from pyzbar.pyzbar import decode; print('pyzbar OK')"
```

---

## 5. Veredicto final

### ¿Se puede desplegar a staging **YA**?

## **Sí condicionado**

**Condición:** staging **monolítico**, **1 réplica** de `api`, entorno **interno/demo** (sin datos reales de tarjetas), con preparación manual de `.env` antes del primer arranque.

### Pasos manuales restantes (obligatorios antes de `compose up`)

| # | Paso | Detalle |
|---|------|---------|
| 1 | **`SECRET_KEY`** | Copiar `.env.example` → `.env`; generar clave real (`python -c "import secrets; print(secrets.token_hex(32))"`) — sin esto la API no arranca |
| 2 | **`CORS_ORIGINS`** | Añadir en `.env` el origen exacto del frontend staging (p. ej. `http://<host>:8080` o URL pública) |
| 3 | **`INTERNAL_API_TOKEN`** | Sustituir `dev-internal-token` por un valor aleatorio único en `.env` |
| 4 | **Alembic (solo si DB vieja)** | Si el volumen `db_data` es anterior al SQL con `tbmovimiento`: `docker compose exec api alembic upgrade head` |
| 5 | **`docker compose up`** | `docker compose build` + `docker compose up -d`; verificar `/health` en `:8080` y `:8000` |

### Fixes ya aplicados en el repo (no requieren acción)

1. **Dockerfile API:** `libzbar0` para pyzbar/QR + copia de `backend/alembic/` y `alembic.ini`.
2. **`GET /api/tarjeta/readOne`:** devuelve `cvc: "***"` (`tarjeta.py` línea 66).
3. **Frontend Vite:** las 9 páginas migradas a TypeScript (`vite.config.ts` + `src/pages/*.ts`).
4. **Backend documentado:** docstrings en módulos `core/` y requisitos `Auth:` en endpoints `routes/`.

### Riesgos aceptados en staging (1 réplica)

- Worker de pagos embebido en el proceso API (OK con una sola réplica).
- Blacklist y rate limit en memoria (se pierden al reiniciar).
- Registro expone CVC **una sola vez** al crear cuenta; PAN visible en dashboard autenticado.
- HTTP plano (sin TLS) — inaceptable para producción expuesta.
- CI no falla si el build Docker se rompe (`continue-on-error: true`).

### Qué sigue siendo insuficiente para producción / fintech expuesto

- HTTPS, blacklist/rate-limit distribuidos (Redis).
- Cifrado de PAN/CVC en BD.
- Tests E2E con MySQL y `docker compose up` en CI.
- Quitar `continue-on-error` en jobs Docker del CI.

---

## Referencias auditadas

- `docker-compose.yml`
- `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`
- `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/*.py`
- `.env.example`, `frontend/vite.config.ts`, `frontend/src/pages/*.ts`
- `.github/workflows/ci.yml`, `requirements.txt`
- `backend/app/api/routes/*.py` (docstrings `Auth:`)
- `backend/alembic/`, `dbflash.sql`
- `docs/SEGURIDAD.md`, `docs/DOCKER.md`

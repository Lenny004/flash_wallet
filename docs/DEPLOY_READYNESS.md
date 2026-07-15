# Auditoría de readiness para despliegue — Flash Wallet v0.2.0

**Fecha:** 2026-07-15  
**Alcance:** solo lectura del repositorio + verificación local parcial (`npm run build` OK; Python/Docker daemon no disponibles en el entorno de auditoría).  
**Criterio:** despliegue a **staging** con `docker compose` en un solo host (réplica única), sin hardening de producción completo.

---

## Resumen ejecutivo

El proyecto tiene una base sólida para staging **monolítico** (compose de 3 servicios, healthchecks, CI con pytest y build de frontend, Pydantic v2, auth en la mayoría de endpoints). Sin embargo, hay **bloqueantes técnicos y de seguridad** que impiden un despliegue confiable “tal cual” hoy.

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
| Decode QR (pyzbar) | **LISTO** | `backend/Dockerfile` instala `libzbar0` antes de `pip install` |
| Migraciones en imagen | PARCIAL | Dockerfile copia solo `backend/app`, no `backend/alembic/` |
| Registro expone PAN/CVC | **PARCIAL** | `POST /api/usuarios/` devuelve `pan` y `cvc` **una vez** (tarjeta_digital.html); documentado en código |
| GET tarjeta expone PAN/CVC | **PARCIAL** | `GET /api/tarjeta/readOne` devuelve `pan` completo; `cvc` enmascarado como `"***"` |
| Blacklist refresh en memoria | PARCIAL | `token_blacklist.py` — se pierde al reiniciar; no compartida entre réplicas |
| Rate limit en memoria | PARCIAL | `rate_limit.py` — mismo problema multi-réplica |
| Legacy `api/` coexistiendo | PARCIAL | Carpeta legacy aún presente; no entra en imagen Docker actual |

### Frontend (Vite)

| Ítem | Estado | Evidencia / notas |
|------|--------|-------------------|
| `npm run build` | LISTO | Verificado localmente (tsc + vite build sin errores) |
| Multi-page build | LISTO | `vite.config.ts` define entradas login/registro/dashboard |
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
| Build API sin libzbar | **LISTO** | `libzbar0` instalado en `backend/Dockerfile` |
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
| Alembic en contenedor API | PARCIAL | No copiado en Dockerfile; upgrades deben correrse fuera del contenedor |
| `alembic upgrade` en entrypoint | BLOQUEANTE (ops) | No hay script de arranque que migre automáticamente |

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
| `SECRET_KEY` con valor real en deploy | **BLOQUEANTE** | `.env.example` tiene placeholder `genera_una_clave_nueva` |
| `INTERNAL_API_TOKEN` fuerte | PARCIAL | Default `dev-internal-token` en `config.py` y `.env.example` |
| CORS restrictivo | PARCIAL | Ya no es `*`; hay que añadir URL exacta de staging |
| PAN/CVC en respuestas API | **PARCIAL** | Registro expone CVC una vez; `readOne` enmascara CVC (`"***"`), PAN visible |
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
| `tbmovimiento` no existe | Error al recargar/debitar | Volumen Docker antiguo creado antes de SQL con ledger | `cd backend && alembic upgrade head` contra la DB |
| Pagos duplicados | Doble débito / facturas repetidas | Varias réplicas API, cada una con `_payments_poll_loop` | Una sola réplica API en staging, o extraer worker a servicio único |

### Seguridad / datos

| Error | Síntoma | Causa raíz | Mitigación |
|-------|---------|------------|------------|
| PAN/CVC en registro | Respuesta JSON visible en DevTools | `POST /api/usuarios/` devuelve `tarjeta.cvc` **una vez** al crear cuenta | Aceptable para demo; CVC no se repite en `readOne` |
| PAN/CVC en dashboard | `GET /api/tarjeta/readOne` | CVC enmascarado (`"***"`); PAN completo para UI de tarjeta | Frontend muestra `"***"` sin cambios |
| Logout inefectivo tras restart | Refresh sigue válido | Blacklist en memoria | Aceptable en staging interno; Redis/DB para prod |
| Rate limit bypass | Fuerza bruta distribuida | Limiter por proceso | Proxy/WAF o Redis |
| Token interno adivinable | Llamadas a `/api/internal/procesar_pagos` | Default `dev-internal-token` | Rotar `INTERNAL_API_TOKEN` en staging |

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
| `backend/Dockerfile` | Repo | Presente |
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
| `backend/alembic.ini` | `alembic upgrade head` desde host con Python |
| `backend/alembic/env.py` | Lee `DATABASE_URL` del `.env` |
| `backend/alembic/versions/001_tbmovimiento.py` | DB sin tabla `tbmovimiento` |

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
# Con MySQL accesible (compose db o XAMPP)
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
# Si falla con ImportError / cannot find libzbar → BLOQUEANTE confirmado
```

---

## 5. Veredicto final

### ¿Se puede desplegar a staging **YA**?

## **No**

### Por qué (orden de severidad)

1. ~~**Imagen API incompleta para QR:**~~ **Resuelto** — `libzbar0` instalado en `backend/Dockerfile`.

2. **Secretos no listos out-of-the-box:** la API **no arranca** sin `SECRET_KEY` real. El `.env.example` trae un placeholder y el compose exige `env_file: .env`. Esto es operacionalmente esperado, pero significa que **no hay deploy “un click”** sin preparación previa.

3. **Exposición PAN/CVC en API (parcial):** registro devuelve CVC una vez; `readOne` enmascara CVC. PAN sigue visible en dashboard (tarjeta digital autenticada). Aceptable para staging interno; no listo para fintech expuesto.

4. **CORS no preparado para staging:** hay que configurar manualmente el origen del frontend desplegado; el default no incluye un host de staging real.

5. **CI no garantiza imágenes Docker:** los jobs de build Docker no fallan el pipeline (`continue-on-error: true`), por lo que una regresión en Dockerfile **no se detecta automáticamente**.

6. **Worker de pagos embebido:** aceptable con **una sola réplica** de `api`; escalar horizontalmente sin cambios causará procesamiento duplicado.

### Qué sí está listo

- Build de frontend Vite (verificado).
- Arquitectura compose con healthchecks y proxy Nginx `/api`.
- Conexión API→MySQL con host `db` en compose.
- Smoke tests de auth y QR intent en CI.
- Esquema SQL semilla con `tbmovimiento`.
- Pydantic v2 y configuración por entorno.

### Camino mínimo para un **“Sí” condicionado** (staging interno, 1 réplica, sin datos reales)

| # | Acción | Esfuerzo estimado |
|---|--------|-------------------|
| 1 | ~~Añadir `libzbar0` en `backend/Dockerfile`~~ | **Hecho** |
| 2 | Crear `.env` staging con `SECRET_KEY`, `INTERNAL_API_TOKEN`, `CORS_ORIGINS` correctos | Bajo |
| 3 | Dejar `VITE_API_URL` vacío en build frontend Docker | Ya OK |
| 4 | Quitar `continue-on-error` en jobs Docker del CI | Bajo |
| 5 | ~~Enmascarar CVC en `readOne`~~; registro puede seguir devolviendo CVC una vez | **Parcial** (readOne OK) |
| 6 | Documentar/ejecutar `alembic upgrade head` solo si el volumen DB es antiguo | Bajo |
| 7 | Desplegar con `docker compose up` en un solo nodo, sin escalar `api` | Operativo |

Con esas correcciones (especialmente **2** y preparación de `.env`), un staging **interno** para demo/QA sería razonable. Para staging expuesto o pre-producción fintech, faltan además enmascarar PAN en registro, HTTPS, blacklist/rate-limit distribuidos y hardening de tokens.

---

## Referencias auditadas

- `docker-compose.yml`
- `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`
- `backend/app/main.py`, `backend/app/core/config.py`
- `.env.example`, `frontend/vite.config.ts`
- `.github/workflows/ci.yml`, `requirements.txt`
- `backend/app/api/routes/usuarios.py`, `tarjeta.py`
- `backend/app/core/token_blacklist.py`, `rate_limit.py`
- `backend/alembic/`, `dbflash.sql`
- `docs/SEGURIDAD.md`, `docs/DOCKER.md`

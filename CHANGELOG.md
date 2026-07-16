# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Añadido

- Guards de sesión unificados (`requireUserSession` / `requireCardSession`) en páginas ES autenticadas.
- `legacy/`: prototipo XAMPP (`api/`, `views/`, `controllers/`, etc.) archivado como referencia histórica.
- Auditoría `docs/DEPLOY_READYNESS.md` (staging: sí condicionado).
- Todas las páginas de negocio migradas a módulos Vite TypeScript.
- CI: builds Docker de API y frontend fallan el pipeline si el Dockerfile está roto.
- `.dockerignore` y `docker-compose.override.yml.example` para hot reload.

### Añadido (sesión anterior)

- Blacklist de refresh tokens en logout (`POST /api/usuarios/logout`): revocación server-side por `jti` en memoria; `POST /api/usuarios/refresh` rechaza tokens revocados.
- Rate limiting en memoria (`app/core/rate_limit.py`): login (5 req/min por IP) y decode QR (20 req/min por `id_tarjeta`).
- `GET /api/servicios/` autenticado con `token_usuario` (`response_model`); guard 401 sin token.
- Tests ampliados: movimientos y crear transacción sin auth, logout/refresh revocado, rate limit unitario, QR intents (firma, TTL, campos requeridos).
- Enums de estado y `ForeignKey` explícitas en el ORM.

### Cambiado

- Stack activo documentado como `backend/` + `frontend/`; legacy fuera de la raíz.
- `escanear.js` / `escanear_servicio.ts`: la transacción se crea solo con el `intent` firmado.
- Scaffolding TypeScript (`frontend/src/lib/auth.ts`, `src/api/client.ts`) como fuente de verdad para `apiFetchAuth` y refresh.
- Dockerfile API: `libzbar0` + Alembic en la imagen; CVC enmascarado en `GET /api/tarjeta/readOne`.

### Documentado

- `docs/SEGURIDAD.md`: rate limit, payment intents QR y blacklist de refresh.
- Docstrings/JSDoc en backend crítico y páginas ES.

### Planeado

- Blacklist de refresh en Redis o DB para multi-réplica.
- Deploy cloud con HTTPS.
- Eliminar carpeta `legacy/` en v0.3.0 si ya no se necesita.

- Unificación de `controllers/*.js` en módulos ES.
- Eliminación de carpetas legacy (`api/`, `views/`, `controllers/`, `css/`).
- Despliegue en cloud (API + frontend estático).
- Guards de sesión unificados en todas las páginas.
- Blacklist de refresh en Redis/DB (hoy solo en memoria del proceso).

## [0.2.0] - 2026-07-14

> Rama `develop`. Profesionalización del prototipo académico hacia un monorepo
> desplegable con backend testeable, seguridad fintech-lite y frontend desacoplado.

### Añadido

- Monorepo documentado: `docs/`, `README.md`, `CONTRIBUTING.md`, `LICENSE` (MIT).
- `.gitignore`, `.env.example` y `requirements.txt` con dependencias fijadas.
- Backend reorganizado en `backend/app/` (routers, models, schemas, services, core).
- `core/config.py` con Pydantic Settings (`SECRET_KEY`, `DATABASE_URL`, CORS, JWT, QR TTL).
- Esqueleto Alembic y migración inicial `tbmovimiento` para el ledger.
- Capa `services/wallet.py` con bloqueo de fila (`with_for_update`) para recargas y débitos.
- Ledger de movimientos (`tbmovimiento`) como audit trail de cambios de saldo.
- Payment intents QR firmados con HMAC y TTL (`services/qr_intent.py`).
- Refresh tokens (`POST /api/usuarios/refresh`) y auto-renovación en el cliente (`auth.js`, `client.ts`).
- Worker de pagos recurrentes en el servidor (lifespan de FastAPI, sin polling desde el navegador).
- Endpoint `/health` con `response_model` para healthchecks de Docker.
- Scaffold frontend `frontend/` con Vite + TypeScript (`src/api/client.ts`, proxy `/api`).
- Copia de HTML/CSS/controllers a `frontend/public/` servidos por Vite.
- Docker Compose end-to-end: `db` + `api` + `frontend` (nginx).
- `Dockerfile` para backend y frontend; documentación en `docs/DOCKER.md`.
- CI en GitHub Actions: `ruff check`, `pytest` (smoke) y `npm run build`.
- Tests de humo y guards de auth (401 sin token); tests de QR intent y refresh.
- `ruff.toml` para lint incremental del backend.
- `api/DEPRECATED.md` con plan de eliminación en v0.3.0.
- Centralización de la URL base de la API en el frontend (`config.js`, `VITE_API_URL`).

### Cambiado

- Secretos (`SECRET_KEY`, `DATABASE_URL`) movidos de código hardcodeado a variables de entorno.
- Búsquedas en historial y facturas: árbol binario en memoria reemplazado por consultas SQL.
- JWT de tarjeta: eliminados PAN y CVC del payload; solo identificadores.
- Endpoints críticos protegidos con JWT (deletes, QR, procesamiento de pagos).
- CORS configurable por `CORS_ORIGINS` en lugar de `allow_origins=["*"]`.
- Respuestas parcialmente estandarizadas con `response_model` (`/health`, `GET /api/usuarios/`).
- Flujo de desarrollo diario en rama `develop`; repo en https://github.com/Lenny004/flash_wallet.

### Corregido

- Sintaxis SQL en `dbflash.sql` (coma faltante en `tbtarjeta_digital`).
- Alineación de `id_usuario` en tarjeta digital legacy con el esquema actual.

### Seguridad

- Rotación de `SECRET_KEY` comprometida; clave nueva solo en `.env` local.
- `procesar_pagos` ya no es un endpoint público invocable desde el navegador.
- QR con firma y expiración para evitar manipulación de montos en el cliente.

### Deprecado

- Carpeta `api/` y stack XAMPP raíz (`views/`, `controllers/`, `css/`) — ver `api/DEPRECATED.md`.

## [0.1.0] - 2025

> Prototipo inicial académico. Funcional pero sin estructura de producto ni controles de
> seguridad para producción.

### Añadido

- API monolítica FastAPI en `api/` con routers por dominio (`api/private/`).
- Modelos SQLAlchemy y schemas Pydantic v1 por tabla.
- Autenticación JWT (usuario y tarjeta) con PyJWT y bcrypt.
- Frontend estático HTML/CSS/JS vanilla servido por XAMPP.
- Flujo completo: registro, login, tarjeta digital, recarga, escaneo QR, pagos recurrentes,
  historial, facturas y perfil de usuario.
- Esquema MySQL `dbflash.sql` con datos semilla.
- Decodificación de QR con pyzbar; alertas UI con SweetAlert2.
- Árbol binario en memoria para búsquedas en historial y facturas.

### Limitaciones conocidas

- Secretos y URLs hardcodeadas en el código fuente.
- Endpoints sensibles sin autenticación ni autorización por propietario.
- PAN y CVC expuestos en el JWT de tarjeta.
- Procesamiento de pagos disparado desde el navegador cada 5 s.
- Sin tests, CI, Docker, migraciones versionadas ni documentación de despliegue.

[Unreleased]: https://github.com/Lenny004/flash_wallet/compare/v0.2.0...develop
[0.2.0]: https://github.com/Lenny004/flash_wallet/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Lenny004/flash_wallet/releases/tag/v0.1.0

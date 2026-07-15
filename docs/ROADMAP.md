# Roadmap de profesionalización

Migración incremental de prototipo a producto. Cada fase es entregable por sí sola: al
terminarla, Flash sigue funcionando y queda en mejor estado que antes.

```mermaid
flowchart LR
  F0["Fase 0: Repo serio"] --> F1["Fase 1: Backend pro"]
  F1 --> F2["Fase 2: Frontend desacoplado"]
  F2 --> F3["Fase 3: Docker + CI"]
  F3 --> F4["Fase 4: Patrones fintech"]
  F4 --> F5["Fase 5: Producto presentable"]
```

## Fase 0 - Repo serio (1-2 días)

Cero cambios funcionales; el objetivo es poder publicar con seguridad.

- [x] Crear `docs/`, `README.md` raíz, `LICENSE` (MIT).
- [x] Crear `.gitignore` y `.env.example`.
- [x] Mover `SECRET_KEY` y `DATABASE_URL` a `.env`; rotar la clave (nueva clave en `.env` local).
- [x] Crear `requirements.txt` con las dependencias actuales.
- [x] Corregir el bug de sintaxis en `dbflash.sql`.
- [x] `git init`, primer commit y push a `origin/develop` en https://github.com/Lenny004/flash_wallet.

**Done:** el proyecto es publicable, sin secretos en el código, con documentación y README.

## Fase 1 - Backend profesional (1-2 semanas)

- [x] Reorganizar `api/` -> `backend/app/` (copiado; `api/` legacy se mantiene temporalmente).
- [x] `core/config.py` con Pydantic Settings.
- [x] Unificar `declarative_base` y declarar Base única.
- [x] Introducir Alembic (esqueleto listo; falta migración inicial generada).
- [ ] Estandarizar respuestas y errores; usar `response_model`.
- [x] Tests con pytest de humo y guards de auth (401 sin token); faltan tests de login/QR con DB.
- [x] `ruff` configurado (`ruff.toml`; lint en CI; sin `--fix` masivo aún).
- [x] Docker Compose solo para MySQL (siguiente paso incremental).

**Done:** backend testeable, con migraciones versionadas y configuración por entorno.

## Fase 2 - Frontend desacoplado (2-3 semanas)

- [x] Crear scaffold `frontend/` con Vite + TypeScript (`apiFetch`, proxy `/api`).
- [ ] Copiar HTML/CSS de `views/` al frontend Vite.
- [ ] Unificar `controllers/*.js` en módulos ES.
- [x] `src/api/client.ts` con `baseURL` desde `VITE_API_URL`.
- [x] Proxy `/api` en `vite.config` hacia `localhost:8000`.
- [ ] Guards de sesión por página.

**Done:** misma UI, sin URLs hardcodeadas, con build reproducible.

## Fase 3 - Docker end-to-end (1 semana)

- [~] `docker-compose.yml`: `db` + `api` (falta servicio frontend/nginx).
- [~] `Dockerfile` multi-stage para backend (existe Dockerfile API; falta frontend).
- [~] `.github/workflows/ci.yml`: lint (ruff) + tests (pytest) + build frontend (falta build Docker API).
- [x] Endpoint `/health` (falta healthcheck en Compose del servicio api).

**Done:** `docker compose up` levanta todo; CI verde en cada PR.

## Fase 4 - Patrones fintech (2-4 semanas, incremental)

- [x] Autenticar endpoints mutables críticos (deletes, procesar_pagos, QR); falta auditoría completa.
- [x] Transacciones atómicas para recarga/débito (`services/wallet.py` + `with_for_update`).
- [ ] Ledger de movimientos (audit trail).
- [ ] QR con expiración / payment intent firmado.
- [x] Quitar pan/cvc del JWT de tarjeta (faltan refresh tokens).
- [ ] Convertir `procesar_pagos` en worker/cron en vez de polling desde el navegador.
- [x] Reemplazar el BST en memoria por consultas SQL.

**Done:** operaciones financieras seguras, auditables y sin endpoints abiertos.

## Fase 5 - Producto presentable (opcional)

- [ ] Migrar páginas críticas (login, dashboard, pago) a React + TanStack Query.
- [ ] Confirmación de pago en tiempo real (WebSocket/SSE).
- [ ] Evaluar PostgreSQL si el despliegue cloud lo requiere.
- [ ] Deploy: Railway/Render/Fly.io (API) + Vercel/Netlify (frontend).
- [ ] CHANGELOG y versionado semántico.

**Done:** Flash desplegado, con dominio, HTTPS y experiencia moderna.

## Prioridades inmediatas (top 5)

1. Sacar `SECRET_KEY` del código (riesgo crítico antes de GitHub).
2. Centralizar la config de API en el frontend.
3. Adoptar `full-stack-fastapi-template` como referencia de estructura.
4. Modelar pagos con ledger + intents (estilo EasyPay) antes de una pasarela real.
5. Docker solo para la base de datos primero (salto mínimo fuera de XAMPP).

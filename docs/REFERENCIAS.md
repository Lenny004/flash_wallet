# Referencias

Repositorios y patrones profesionales para inspirar la evolución de Flash.

## Repositorios de referencia

### full-stack-fastapi-template
<https://github.com/fastapi/full-stack-fastapi-template>

Blueprint oficial production-ready. Qué adoptar:
- Estructura `backend/app/` con `api/`, `models/`, `schemas/`, `core/config.py`, `crud/`, `alembic/`.
- Docker Compose (API + DB + frontend).
- JWT, hashing de contraseñas, Pydantic Settings para variables de entorno.
- CI con GitHub Actions (lint, tests, build).
- Cliente TypeScript autogenerado desde OpenAPI.

Es la referencia más directa porque el stack de Flash ya es ~70% compatible.

### EasyPay
<https://github.com/Reagan-dev/EasyPay>

Patrón "billetera cerrada + pagos QR". Qué adoptar:
- Ledger interno (saldo en DB, transacciones atómicas, audit trail).
- Payment intents con QR de corta duración (expiran en segundos).
- JWT access + refresh + blacklist en logout.
- Separación por dominios (`wallets/`, `payments/`, `accounts/`).

### CampusEats
<https://github.com/Gopal7387/CampusEats>

Flujo estudiante -> recarga -> QR -> pago, casi idéntico al escaneo de servicios de Flash.
Qué adoptar:
- QR con expiración (5 min) en vez de payload permanente.
- Roles separados (usuario, vendor, admin).
- Migración gradual de frontend con Tailwind.

### digital-wallet-POC
<https://github.com/Akobabs/digital-wallet-POC>

POC pequeño y legible. Qué adoptar:
- Estructura mínima `backend/` + `frontend/` con README de setup.
- Endpoints de wallet, historial, generación/escaneo QR.
- Capa `services/` separada del router.

### flask-websocket (payment confirm)
<https://github.com/Schlickmann/flask-websocket>

Confirmación de pago en tiempo real. Qué adoptar:
- Flujo crear pago -> mostrar QR -> confirmar vía WebSocket (sin polling).
- Tests con pytest sobre endpoints de pago.
- Patrón callback de confirmación (simula pasarela real).

## Qué NO copiar todavía

- Microservicios, Redis, Kubernetes.
- Blockchain / Web3.
- Integración con pasarela de pago real.

Son referencias de arquitectura avanzada, no necesidades del Flash actual. Se reevalúan
cuando el núcleo esté profesionalizado (post Fase 4).

## Mapa de inspiración por área de Flash

| Área de Flash | Referencia | Mejora concreta |
|---------------|------------|-----------------|
| Estructura del repo | full-stack-fastapi-template | Monorepo, Docker, CI |
| Recarga / débito de saldo | EasyPay | Ledger + transacciones atómicas |
| Escaneo QR | CampusEats, EasyPay | QR con expiración / intent |
| Login / tokens | EasyPay, full-stack-template | Access + refresh |
| Confirmación de pago | flask-websocket | Tiempo real sin polling |
| Frontend gradual | full-stack-template | TypeScript + tipos desde OpenAPI |

# Seguridad

Este documento lista los riesgos detectados y su remediación. **Debe atenderse la sección
"Bloqueantes antes de publicar" antes de subir el repositorio a GitHub.**

## Bloqueantes antes de publicar

### 1. Secretos hardcodeados en el código

- Había una `SECRET_KEY` hardcodeada en
  [api/helpers/tokens.py](../api/helpers/tokens.py) y duplicada en varios routers
  (`api_usuarios.py`, `api_historial.py`, `api_tarjeta.py`). Esa clave se considera
  **comprometida** y debe rotarse; el valor concreto no se documenta aquí.
- La cadena de conexión a MySQL estaba hardcodeada en
  [api/helpers/database.py](../api/helpers/database.py).

**Remediación:**
1. Mover ambos a variables de entorno leídas con Settings (`api/helpers/config.py`).
2. Generar una clave nueva con `python -c "import secrets; print(secrets.token_hex(32))"`.
3. Definir un único punto de verdad para la clave (no duplicarla en cada archivo).
4. Nunca commitear `.env`; publicar solo `.env.example` con placeholders.

### 2. Endpoints sensibles sin autenticación

| Endpoint | Riesgo |
|----------|--------|
| `GET /api/usuarios/` | Expone todos los usuarios (incluye hash de contraseña) |
| `POST /api/historial/delete` | Borrado arbitrario de historial |
| `POST /api/factura/delete` | Borrado arbitrario de facturas |
| `POST /api/transaccion/procesar_pagos` | Operación financiera invocable por cualquiera |
| `POST /api/decode_qr/` | Lectura de datos de servicios sin sesión |

**Remediación:** exigir JWT en todos los endpoints mutables y de datos, autorizar por
propietario del recurso (la tarjeta/usuario del token debe coincidir con el recurso), y
convertir `procesar_pagos` en tarea de servidor (worker/cron) autenticada, no un endpoint
público llamado desde el navegador.

### 3. Datos sensibles dentro del JWT

El `token_tarjeta` incluye **PAN y CVC** en su payload y se devuelven en registro/login.
Un JWT solo está firmado, no cifrado: cualquiera que lo tenga lee su contenido.

**Remediación:** el token debe contener solo identificadores (`id_tarjeta`, `id_usuario`).
El PAN se muestra enmascarado y el CVC nunca se expone ni se almacena en claro.

## Otros riesgos

### CORS demasiado permisivo

`allow_origins=["*"]` junto con `allow_credentials=True` en [api/api.py](../api/api.py) es una
combinación problemática. Restringir a los orígenes concretos del frontend vía
`CORS_ORIGINS` en `.env`.

### Tokens en localStorage

Los JWT se guardan en `localStorage`, vulnerable a XSS. Mitigaciones:
- Sanitizar toda inserción de datos de API en el DOM (evitar `innerHTML` con datos crudos).
- Evaluar cookies `httpOnly` + `SameSite` para el refresh token.

### Validación desigual

La validación fuerte está en el cliente (`componentes.js`); el backend usa Pydantic de forma
inconsistente y mezcla respuestas (`HTTPException` vs `{"estado": 0}`). Estandarizar:
validación en backend con Pydantic v2 y `response_model`, y formato de error uniforme.

### QR sin firma ni expiración

~~El QR es un string separado por `@` que incluye `monto` e `id_estado`; el cliente puede
manipular campos antes de crear la transacción.~~ **Remediado en v0.2** — ver sección
[Payment intents QR](#payment-intents-qr) más abajo.

## Controles implementados (v0.2+)

### Rate limiting

Limiter en memoria en [`backend/app/core/rate_limit.py`](../backend/app/core/rate_limit.py):
ventana deslizante por clave; al superar el límite responde **429** con
`"Demasiadas solicitudes. Intenta más tarde."`.

| Endpoint | Clave | Límite | Ventana |
|----------|-------|--------|---------|
| `POST /api/usuarios/login` | `login:{client_ip}` | 5 | 60 s |
| `POST /api/decode_qr/` | `qr:{id_tarjeta}` | 20 | 60 s |

**Limitaciones actuales:**

- El estado vive en el proceso de la API: se pierde al reiniciar y no se comparte entre
  réplicas. En producción usar Redis o un proxy (nginx, Cloudflare) con rate limit global.
- `decode_qr` exige JWT de tarjeta; el límite es por titular, no por IP anónima.

Tests: [`backend/tests/test_rate_limit.py`](../backend/tests/test_rate_limit.py).

### Payment intents QR

Flujo firmado en [`backend/app/services/qr_intent.py`](../backend/app/services/qr_intent.py):

1. Tras decodificar el QR, `POST /api/decode_qr/` devuelve un objeto `intent` con
   `id_servicio`, `monto`, `frecuencia`, `descripcion`, `exp` (unix) y `sig` (HMAC-SHA256
   sobre una cadena canónica, usando `SECRET_KEY`).
2. El TTL por defecto es `QR_INTENT_TTL_SECONDS` (300 s en
   [`backend/app/core/config.py`](../backend/app/core/config.py)).
3. `POST /api/transaccion/crear` llama a `verificar_intent()` antes de persistir: rechaza
   intents expirados, con firma incorrecta o con campos faltantes (**400**).
4. El frontend (`controllers/escanear.js`) guarda el `intent` del decode y solo envía
   `exp`/`sig` al crear; no acepta montos editados manualmente sin QR válido.

**Qué mitiga:** manipulación de montos o servicio en el cliente entre escaneo y cobro.

Tests: [`backend/tests/test_qr_intent.py`](../backend/tests/test_qr_intent.py),
[`backend/tests/test_auth_endpoints.py`](../backend/tests/test_auth_endpoints.py) (401 sin token en decode/crear).

### Blacklist de refresh tokens

Implementación en [`backend/app/core/token_blacklist.py`](../backend/app/core/token_blacklist.py)
e integrada en [`backend/app/core/security.py`](../backend/app/core/security.py):

- Cada refresh token incluye un `jti` único (`new_jti()` al emitir en login).
- `POST /api/usuarios/logout` con `{ "refresh_token": "..." }` extrae el `jti` y lo añade
  a un `set` en memoria (`revoke`).
- `verificar_refresh_token()` consulta `is_revoked()` antes de renovar access tokens; un
  token revocado devuelve **401** (`"Token revocado."`).
- El cliente (`controllers/auth.js`, `componentes.js`) llama a `revokeRefreshToken()` al
  cerrar sesión y borra `localStorage`; la revocación efectiva depende del logout server-side.

**Limitaciones actuales:**

- La blacklist es **por proceso**: un reinicio de la API la vacía; en despliegue multi-réplica
  un token revocado en un worker podría seguir válido en otro hasta migrar a Redis o tabla
  `revoked_tokens`.
- Logout no exige JWT de usuario (solo el refresh); un atacante con el refresh podría
  revocar la sesión de la víctima (denegación de servicio menor). Valorar exigir auth en
  logout en versiones posteriores.

Tests: `test_logout_revoca_refresh_token` en
[`backend/tests/test_auth_endpoints.py`](../backend/tests/test_auth_endpoints.py).

## Checklist de seguridad mínima (fintech-lite)

- [ ] Secretos solo en `.env`, `SECRET_KEY` rotada
- [ ] Contraseñas con bcrypt (verificar que no haya texto plano en DB)
- [ ] JWT access corto + refresh; sin datos sensibles en el payload
- [ ] Todos los endpoints mutables autenticados y autorizados por propietario
- [ ] CORS restringido a orígenes conocidos
- [ ] Débito de saldo en transacción atómica con validación previa
- [x] QR firmado o con TTL (payment intents HMAC + `verificar_intent` en crear)
- [x] Rate limiting en login y decode QR (limiter en memoria; valorar Redis/`slowapi` en prod)
- [x] Blacklist de refresh en logout (memoria por `jti`; migrar a Redis/DB en prod)
- [ ] Sanitización de datos en el DOM
- [ ] HTTPS en despliegue

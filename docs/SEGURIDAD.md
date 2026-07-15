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

El QR es un string separado por `@` que incluye `monto` e `id_estado`; el cliente puede
manipular campos antes de crear la transacción.

**Remediación:** firmar el contenido del QR (HMAC) o usar payment intents con TTL corto
(estilo EasyPay), validando en el servidor que el intent existe y no expiró.

## Checklist de seguridad mínima (fintech-lite)

- [ ] Secretos solo en `.env`, `SECRET_KEY` rotada
- [ ] Contraseñas con bcrypt (verificar que no haya texto plano en DB)
- [ ] JWT access corto + refresh; sin datos sensibles en el payload
- [ ] Todos los endpoints mutables autenticados y autorizados por propietario
- [ ] CORS restringido a orígenes conocidos
- [ ] Débito de saldo en transacción atómica con validación previa
- [ ] QR firmado o con TTL
- [ ] Rate limiting en login y decode QR (p. ej. `slowapi`)
- [ ] Sanitización de datos en el DOM
- [ ] HTTPS en despliegue

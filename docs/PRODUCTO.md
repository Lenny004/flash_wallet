# Producto

## Visión

**Flash** es una billetera digital (wallet cerrada) que permite a un usuario pagar
servicios recurrentes (telefonía, internet, gas, agua, electricidad) desde una
tarjeta virtual, recargando saldo y escaneando códigos QR de cada servicio.

La visión a mediano plazo es convertir el prototipo en una plataforma fintech-lite
segura y desplegable, con un ledger de saldo confiable, pagos QR con expiración,
autenticación robusta y experiencia de usuario en tiempo real.

## Dominio de negocio

El producto está orientado inicialmente a servicios de El Salvador (los datos semilla
incluyen Claro, Tigo, Movistar, Tropigas, ANDA, AES y DELSUR, y los formularios usan
prefijo `+503`).

Conceptos clave:

- **Usuario:** persona registrada con credenciales y datos de contacto.
- **Tarjeta digital:** instrumento virtual (PAN, CVC, saldo) creado automáticamente al registrarse.
- **Recarga / historial:** ingreso de saldo a la tarjeta (depósitos).
- **Servicio:** proveedor pagable (telecom, utility).
- **Transacción:** pago recurrente asociado a un servicio, con frecuencia y estado.
- **Factura:** comprobante generado cuando una transacción se procesa con éxito.
- **Estado:** ciclo de vida de una transacción (Pendiente, En espera, Completada).

## Usuarios objetivo

| Rol | Hoy | Objetivo |
|-----|-----|----------|
| Usuario final | Registro, recarga, escaneo QR, pago de servicios | + verificación, notificaciones, historial exportable |
| Administrador | No existe | Gestión de servicios, monitoreo de transacciones |
| Proveedor de servicio | Solo dato semilla | (Futuro) portal para emitir QR y conciliar pagos |

## Features actuales

- Registro e inicio de sesión de usuarios.
- Creación automática de tarjeta digital (PAN + CVC + saldo).
- Recarga de saldo simulando una tarjeta externa.
- Escaneo de imagen QR para dar de alta un pago de servicio.
- Procesamiento automático de pagos recurrentes por frecuencia y fecha.
- Historial de depósitos (recargas) y de facturas (pagos completados).
- Búsqueda en historial y facturas.
- Perfil de usuario editable y cierre de sesión.

## Features objetivo (incrementales)

- Autenticación con JWT de acceso corto + refresh token.
- Ledger de saldo con transacciones atómicas y trazabilidad (audit trail).
- QR de pago con expiración (payment intent) en lugar de payload permanente.
- Confirmación de pago en tiempo real (WebSocket/SSE) en vez de polling abierto.
- Panel de administración de servicios y estados.
- Exportación de facturas (PDF/CSV) y notificaciones.
- Despliegue en la nube con dominio y HTTPS.

## Límites de alcance (por ahora no)

- Integración con pasarela de pago real (Stripe, etc.).
- Microservicios, Redis, Kubernetes o blockchain/Web3.
- Aplicación móvil nativa.

Estos quedan fuera del roadmap inmediato para evitar sobre-ingeniería; se reconsiderarán
cuando el núcleo esté profesionalizado.

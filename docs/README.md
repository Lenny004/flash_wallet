# Documentación de Flash

Esta carpeta contiene el plan de escalado de **Flash**, una billetera digital para el pago
de servicios (telecomunicaciones y utilities) mediante tarjeta virtual, escaneo de códigos QR,
recargas de saldo, transacciones recurrentes y facturación.

El objetivo de esta documentación es llevar el proyecto de un prototipo académico
(FastAPI + HTML/JS vanilla + MySQL sobre XAMPP) a un producto profesional, versionado,
contenedorizado y publicable en GitHub, sin reescribir todo de golpe.

## Índice

| Documento | Contenido |
|-----------|-----------|
| [PRODUCTO.md](PRODUCTO.md) | Visión, dominio de negocio, usuarios y features actuales vs. objetivo |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Diagramas actual y objetivo, capas, flujos de negocio |
| [STACK.md](STACK.md) | Tecnologías actuales, stack objetivo 2025-2026 y justificación |
| [BASE_DATOS.md](BASE_DATOS.md) | Modelo entidad-relación, fixes de SQL, migraciones con Alembic |
| [SEGURIDAD.md](SEGURIDAD.md) | Checklist de riesgos críticos y remediaciones priorizadas |
| [DEPLOY_READYNESS.md](DEPLOY_READYNESS.md) | Auditoría de readiness para despliegue (staging/prod) |
| [DOCKER.md](DOCKER.md) | Contenedorización, docker-compose, variables de entorno |
| [GITHUB.md](GITHUB.md) | Nombre, descripción, topics, licencia, CI y publicación del repo |
| [ROADMAP.md](ROADMAP.md) | Fases 0-5 de migración con criterios de done |
| [REFERENCIAS.md](REFERENCIAS.md) | Repositorios similares y qué adoptar de cada uno |

## Cómo usar esta documentación

1. Lee [PRODUCTO.md](PRODUCTO.md) para entender qué es Flash y hacia dónde va.
2. Revisa [SEGURIDAD.md](SEGURIDAD.md) **antes** de publicar el repositorio: hay secretos
   hardcodeados que deben rotarse y sacarse del código.
3. Sigue [ROADMAP.md](ROADMAP.md) fase por fase; cada fase es entregable e incremental.
4. Consulta [GITHUB.md](GITHUB.md) cuando estés listo para crear el repositorio remoto.

## Estado del proyecto

- **Backend:** FastAPI + SQLAlchemy + PyJWT + Pydantic (funcional).
- **Frontend:** HTML + JavaScript vanilla servido por XAMPP.
- **Base de datos:** MySQL `dbflash`.
- **Infraestructura:** pendiente (Docker, CI, tests, README profesional).

Versión objetivo inicial: `v0.1.0`.

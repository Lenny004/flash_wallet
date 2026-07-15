# Flash

**Versión: 0.2.0 (develop)**

Billetera digital con tarjeta virtual para el pago de servicios (telecomunicaciones y
utilities) mediante escaneo de códigos QR, recargas de saldo, transacciones recurrentes
y facturación.

> Estado: profesionalización en curso (Fases 0–4 completadas en `develop`). Consulta el
> plan completo en [docs/](docs/README.md) y el historial en [CHANGELOG.md](CHANGELOG.md).

## Características

- Registro e inicio de sesión de usuarios.
- Tarjeta digital (PAN, CVC, saldo) creada automáticamente al registrarse.
- Recarga de saldo.
- Escaneo de QR para dar de alta pagos de servicios.
- Procesamiento automático de pagos recurrentes.
- Historial de depósitos y de facturas, con búsqueda.
- Perfil de usuario editable.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | FastAPI + SQLAlchemy + PyJWT + Pydantic (`backend/app/`) |
| Base de datos | MySQL 8 |
| Frontend | Vite + TypeScript (`frontend/`); HTML/CSS/JS legacy en transición |

Detalle y evolución del stack en [docs/STACK.md](docs/STACK.md).

## Estructura

```
Flash/
├── backend/        # Backend activo (FastAPI, modelos, schemas, tests)
├── frontend/       # Frontend activo (Vite + páginas HTML estáticas)
├── api/            # Legacy — ver api/DEPRECATED.md (se elimina en v0.3.0)
├── views/          # Legacy (XAMPP)
├── controllers/    # Legacy (XAMPP)
├── css/            # Legacy (XAMPP)
├── resources/      # Librerías de terceros
├── docs/           # Documentación y plan de escalado
└── dbflash.sql     # Esquema y datos semilla
```

## Puesta en marcha (desarrollo)

Requisitos: Python 3.12+, Node.js 18+, MySQL 8 (o XAMPP).

> Trabajo en la rama **`develop`**. No se hace push directo a `main`.
> Repo: https://github.com/Lenny004/flash_wallet
> Guía de contribución: [CONTRIBUTING.md](CONTRIBUTING.md)

1. Crear la base de datos importando `dbflash.sql`.
2. Copiar `.env.example` a `.env` y ajustar los valores (sobre todo `SECRET_KEY`).

### Backend (`backend/app/`)

```bash
cd backend
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Vite)

```bash
cd frontend
npm install
npm run dev
```

Abrir [http://localhost:5173](http://localhost:5173) — redirige a `/pages/login.html`.

### Legacy (`api/` + XAMPP)

Solo para compatibilidad durante la migración. Ver [api/DEPRECATED.md](api/DEPRECATED.md).

```bash
cd api
pip install -r ../requirements.txt
uvicorn api:app --reload
```

Documentación interactiva: `http://127.0.0.1:8000/docs`.
Healthcheck: `http://127.0.0.1:8000/health`.

## Seguridad

Antes de publicar o desplegar, revisa [docs/SEGURIDAD.md](docs/SEGURIDAD.md). Hay secretos
que deben moverse a `.env` y rotarse, y endpoints que requieren autenticación.

## Documentación

- [Producto](docs/PRODUCTO.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Stack](docs/STACK.md)
- [Base de datos](docs/BASE_DATOS.md)
- [Seguridad](docs/SEGURIDAD.md)
- [Docker](docs/DOCKER.md)
- [GitHub](docs/GITHUB.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Referencias](docs/REFERENCIAS.md)

## Licencia

MIT (pendiente de añadir archivo `LICENSE`).

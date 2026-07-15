# Flash — frontend (Vite + HTML estático)

Fase 2: páginas HTML legacy servidas por Vite, sin React.

## Estructura

```
frontend/
├── index.html              # Entrada Vite → redirige a /pages/login.html
├── public/                 # Assets estáticos (publicDir)
│   ├── pages/              # Vistas HTML (copia de views/)
│   ├── css/                # Estilos (copia de css/)
│   ├── controllers/        # JS de la app (copia de controllers/)
│   ├── resources/          # Imágenes, iconos, libs JS (copia de resources/)
│   └── fonts/              # Fuentes (copia de fonts/)
├── src/                    # Scaffold TypeScript (opcional, no usado por las páginas)
├── vite.config.ts          # Proxy /api → http://127.0.0.1:8000
└── package.json
```

Las carpetas `views/`, `css/`, `controllers/`, `resources/` y `fonts/` en la raíz del repo siguen existiendo para XAMPP legacy.

## Requisitos

- Node.js 18+
- API FastAPI en `http://127.0.0.1:8000` (uvicorn / Docker)

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # opcional; vacío usa el proxy de Vite
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173) — redirige a `/pages/login.html`.

## Rutas en desarrollo

| Ruta | Contenido |
|------|-----------|
| `/pages/*.html` | Páginas de la app |
| `/css/*` | Hojas de estilo |
| `/controllers/*` | Scripts JS |
| `/resources/*` | Imágenes, iconos, sweetalert2, etc. |
| `/fonts/*` | Fuente Inter |
| `/api/*` | Proxy a FastAPI (puerto 8000) |

Los HTML usan rutas absolutas (`/css/`, `/controllers/`, `/resources/`). Los enlaces entre páginas son relativos dentro de `/pages/` (p. ej. `dashboard.html`).

## API base

En `public/controllers/config.js`:

```js
window.FLASH_API_BASE = window.FLASH_API_BASE || '';
```

Vacío = las peticiones van a `/api/...` y Vite las reenvía al backend.

## Proxy a la API

En desarrollo, las peticiones a `/api/*` se reenvían a `http://127.0.0.1:8000` vía `vite.config.ts`.

- Deja `VITE_API_URL` vacío en `.env` y usa rutas como `/api/...` (recomendado en dev).
- O define `VITE_API_URL=http://localhost:8000` para llamar a la API directamente.

## Scripts

| Comando           | Descripción                    |
|-------------------|--------------------------------|
| `npm run dev`     | Servidor de desarrollo         |
| `npm run build`   | Typecheck + build estático     |
| `npm run preview` | Previsualizar el build         |

## Cómo probar

1. Arranca la API: `uvicorn` en `backend/` o `docker compose up` (puerto 8000).
2. En otra terminal: `cd frontend && npm run dev`.
3. Abre `http://localhost:5173` → login.
4. Verifica que cargan CSS, fuentes e imágenes (pestaña Red del navegador).
5. Inicia sesión; las llamadas deben ir a `/api/...` (proxy activo).

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
├── src/                    # Módulos ES (migración gradual; ver plan abajo)
│   ├── lib/auth.ts         # refreshAccessTokens, apiFetchAuth (fuente de verdad TS)
│   ├── api/client.ts       # apiFetch para código nuevo (reutiliza lib/auth)
│   ├── main.ts             # Bridge temporal window.* (solo index.html)
│   ├── demo/refresh.ts     # Demo opcional de módulos ES en index.html
│   └── pages/              # Futuros entry points por página (ver src/pages/README.md)
├── vite.config.ts          # Proxy /api → http://127.0.0.1:8000
└── package.json
```

El prototipo XAMPP original (`views/`, `css/`, `controllers/`, `resources/`, `fonts/`, `api/`) está archivado en [`../legacy/`](../legacy/README.md) en la raíz del repo.

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

## Migración a módulos ES (en curso)

Las páginas en `public/pages/` siguen usando scripts globales (`<script src="/controllers/...">`). La migración es **gradual** para no romper `auth.js`, jQuery ni el orden de carga actual.

### Fase actual — scaffolding

| Pieza | Rol |
|-------|-----|
| `src/lib/auth.ts` | Lógica de `refreshAccessTokens` y `apiFetchAuth` (equivalente TS de `public/controllers/auth.js`) |
| `src/api/client.ts` | `apiFetch` para código nuevo; importa `refreshAccessTokens` desde `lib/auth` |
| `src/main.ts` | Expone `window.apiFetchAuth` / `window.refreshAccessTokens` como bridge temporal |
| `index.html` | Carga `main.ts` + demo opcional `src/demo/refresh.ts` |

### Limitación importante

`index.html` (entrada Vite) carga `main.ts`, pero **`/pages/*.html` no**. El bridge `window.*` no llega a las páginas legacy. Hasta migrar cada HTML, esas páginas siguen usando `public/controllers/auth.js`.

### Próximos pasos

1. Migrar una página a la vez → ver [`src/pages/README.md`](src/pages/README.md).
2. Sustituir `<script src="/controllers/auth.js">` por `import` desde `src/lib/auth.ts`.
3. Cuando ninguna página use `auth.js`, eliminar el duplicado en `public/controllers/`.

### Probar el scaffold en dev

```bash
npm run dev
```

Abre `http://localhost:5173` (antes de la redirección automática, o en la consola del navegador):

- Debe aparecer `[Flash ES] auth.ts cargado; refreshAccessTokens disponible`.
- En consola: `await window.__flashRefreshDemo()` (solo si hay `refresh_token` en localStorage).

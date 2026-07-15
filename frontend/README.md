# Flash — frontend (Vite + TypeScript)

Scaffold de la Fase 2: frontend desacoplado con Vite, sin React aún.

## Requisitos

- Node.js 18+
- API FastAPI en `http://127.0.0.1:8000` (XAMPP / uvicorn)

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # opcional; vacío usa el proxy de Vite
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173).

## Proxy a la API

En desarrollo, las peticiones a `/api/*` se reenvían a `http://127.0.0.1:8000` vía `vite.config.ts`.

- Deja `VITE_API_URL` vacío en `.env` y usa rutas como `/api/...` (recomendado en dev).
- O define `VITE_API_URL=http://localhost:8000` para llamar a la API directamente.

## Scripts

| Comando        | Descripción              |
|----------------|--------------------------|
| `npm run dev`  | Servidor de desarrollo   |
| `npm run build`| Typecheck + build estático |
| `npm run preview` | Previsualizar el build |

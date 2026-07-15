# API legacy (`api/`)

> **Esta carpeta está obsoleta.** El código activo vive en `backend/app/`.
> Se eliminará en la versión **v0.3.0**.

## ¿Por qué existe todavía?

Durante la Fase 1 del roadmap se copió `api/` → `backend/app/` para migrar sin romper
el prototipo. La carpeta original se mantiene temporalmente por compatibilidad con
desarrollo local en XAMPP y scripts antiguos.

## Stack actual (usar esto)

| Capa | Ubicación |
|------|-----------|
| Backend | `backend/app/` (FastAPI) |
| Frontend | `frontend/` (Vite + TypeScript) |
| Base de datos | MySQL 8 (`dbflash.sql` / Alembic) |

## Cómo arrancar el nuevo stack

1. Crear la base de datos importando `dbflash.sql`.
2. Copiar `.env.example` a `.env` en la raíz del repo y ajustar `SECRET_KEY` y `DATABASE_URL`.
3. Backend:

   ```bash
   cd backend
   pip install -r ../requirements.txt
   uvicorn app.main:app --reload
   ```

4. Frontend (otra terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. Abrir [http://localhost:5173](http://localhost:5173).

Documentación interactiva de la API: `http://127.0.0.1:8000/docs`.

## Si aún necesitas `api/` (solo transición)

```bash
cd api
pip install -r ../requirements.txt
uvicorn api:app --reload
```

No añadas funcionalidad nueva aquí. Cualquier cambio debe ir en `backend/app/`.

## Eliminación planificada

- **v0.3.0:** se borra `api/` y las carpetas raíz legacy (`views/`, `controllers/`, `css/`, etc.) cuando el frontend Vite cubra todo el flujo.
- Consulta [docs/ROADMAP.md](../docs/ROADMAP.md) para el estado de la migración.

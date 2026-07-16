# Código legacy (solo referencia histórica)

> **Esta carpeta no forma parte del stack activo.** El código en producción y desarrollo
> vive en `backend/` y `frontend/`. Todo lo que hay aquí es el prototipo original (XAMPP +
> FastAPI monolítico) conservado únicamente como archivo histórico.

## Contenido

| Carpeta | Descripción |
|---------|-------------|
| `api/` | Backend FastAPI original (copiado a `backend/app/` en Fase 1) |
| `views/` | Páginas HTML servidas directamente por Apache/XAMPP |
| `controllers/` | Scripts JS globales del prototipo |
| `css/` | Estilos del prototipo |
| `fonts/` | Fuente Inter (copia en `frontend/public/fonts/`) |
| `resources/` | Imágenes, iconos y libs de terceros (copia en `frontend/public/resources/`) |

## Stack actual (usar esto)

| Capa | Ubicación |
|------|-----------|
| Backend | `backend/app/` (FastAPI) |
| Frontend | `frontend/` (Vite + TypeScript) |
| Base de datos | MySQL 8 (`dbflash.sql` / Alembic) |
| Docker | `docker-compose.yml` — servicios `db`, `api`, `frontend` |

## Cómo arrancar el stack activo

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

Con Docker: `docker compose up` (ver [docs/DOCKER.md](../docs/DOCKER.md)).

## Reglas

- **No añadas funcionalidad nueva aquí.** Cualquier cambio debe ir en `backend/app/` o `frontend/`.
- **No modifiques rutas ni imports** salvo que estés estudiando el historial del proyecto.
- Esta carpeta **no entra** en las imágenes Docker ni en el build de Vite.

## Eliminación planificada

- **v0.3.0:** se eliminará `legacy/` por completo cuando el frontend Vite cubra todo el flujo.
- Consulta [docs/ROADMAP.md](../docs/ROADMAP.md) para el estado de la migración.

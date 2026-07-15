# Docker y contenedorización

## Objetivo

Que cualquier persona pueda levantar todo Flash con un solo comando, sin instalar XAMPP:

```bash
docker compose up
```

Esto levanta `db`, `api` y `frontend`. La app queda disponible en **http://localhost:8080** (Nginx sirve el frontend y hace proxy de `/api` hacia la API).

Para levantar solo base de datos y API:

```bash
docker compose up db api
```

Servicios:

- `db`: MySQL 8 con el esquema y datos semilla.
- `api`: FastAPI (uvicorn) conectada a `db`.
- `frontend`: Nginx sirviendo el build estático de Vite (Fase 3).

```mermaid
flowchart LR
  Dev["docker compose up"] --> DB["db: MySQL 8"]
  Dev --> API["api: FastAPI"]
  Dev --> FE["frontend: Nginx"]
  API --> DB
  FE -->|"/api proxy"| API
```

## Fase 3a: solo la base de datos (salto mínimo desde XAMPP)

Primer paso: mover únicamente MySQL a Docker y seguir corriendo la API en local con hot reload.

```yaml
services:
  db:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
      - ./dbflash.sql:/docker-entrypoint-initdb.d/001_schema.sql:ro
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db_data:
```

## Fase 3b: API contenedorizada

`backend/Dockerfile` usa el **contexto de build en la raíz del repo** (porque `requirements.txt` está ahí):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Servicio `api` en `docker-compose.yml`:

```yaml
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file: .env
    environment:
      DATABASE_URL: mysql+pymysql://root:${MYSQL_ROOT_PASSWORD:-flash_dev}@db:3306/${MYSQL_DATABASE:-dbflash}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
```

Sin volúmenes de código en el compose principal (producción). Para hot reload en desarrollo, usar `docker-compose.override.yml`.

## Fase 3c: frontend con Nginx

`frontend/Dockerfile` usa el **contexto de build en la raíz del repo** (igual que `backend/Dockerfile`):

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

`frontend/nginx.conf` sirve estáticos, hace proxy de `/api/` a `http://api:8000/api/`, proxy de `/health` a `http://api:8000/health`, y usa `try_files` para rutas SPA.

Servicio `frontend` en `docker-compose.yml`:

```yaml
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    ports:
      - "8080:80"
    depends_on:
      api:
        condition: service_healthy
```

Acceso: **http://localhost:8080**

## Variables de entorno

Todas viven en `.env` (no versionado). Ver [.env.example](../.env.example) en la raíz.

| Variable | Ejemplo | Uso |
|----------|---------|-----|
| `MYSQL_ROOT_PASSWORD` | `cambia_esto` | Password root de MySQL |
| `MYSQL_DATABASE` | `dbflash` | Nombre de la base |
| `DATABASE_URL` | `mysql+pymysql://root:cambia_esto@db/dbflash` | Conexión del backend |
| `SECRET_KEY` | (token_hex 32) | Firma de JWT (rotada) |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos |
| `JWT_EXPIRE_MINUTES` | `15` | Expiración del access token |
| `VITE_API_URL` | `http://localhost:8000` | Base URL del frontend |

## Healthchecks

- `db`: `mysqladmin ping`.
- `api`: `GET /health` vía Python (`urllib.request`).
- El compose usa `depends_on` con `condition: service_healthy` para que `api` espere a `db` y `frontend` espere a `api`.

## override para desarrollo

Copia `docker-compose.override.yml.example` a `docker-compose.override.yml` para activar hot reload en local.

`docker-compose.override.yml` monta volúmenes de código y activa `--reload` para hot reload
en desarrollo, sin afectar la configuración de producción.

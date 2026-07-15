FROM python:3.12-slim
WORKDIR /app

# Dependencia nativa para pyzbar (decodificación de códigos QR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
# Incluye Alembic para poder ejecutar migraciones dentro del contenedor
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

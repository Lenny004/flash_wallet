import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.factura import routerFactura
from app.api.routes.historial import routerHistorial
from app.api.routes.internal import routerInternal
from app.api.routes.qr import routerQR
from app.api.routes.servicios import routerServicios
from app.api.routes.tarjeta import routerTarjeta
from app.api.routes.transaccion import routerTransaccion
from app.api.routes.usuarios import routerUsuario
from app.core.config import settings
from app.schemas.common import HealthResponse
from app.db.session import SessionLocal
from app.services.payments_worker import procesar_pagos_todas_tarjetas

logger = logging.getLogger(__name__)


async def _payments_poll_loop() -> None:
    while True:
        db = SessionLocal()
        try:
            tarjetas = procesar_pagos_todas_tarjetas(db)
            if tarjetas:
                logger.info("Pagos procesados para %d tarjeta(s)", tarjetas)
        except Exception:
            logger.exception("Error en el worker de pagos")
        finally:
            db.close()
        await asyncio.sleep(settings.payments_poll_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_payments_poll_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Flash Wallet", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "X-Internal-Token"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "error"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
    }


app.include_router(routerUsuario, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(routerHistorial, prefix="/api/historial", tags=["Historial"])
app.include_router(routerTarjeta, prefix="/api/tarjeta", tags=["Tarjeta"])
app.include_router(routerQR, prefix="/api/decode_qr", tags=["QR"])
app.include_router(routerTransaccion, prefix="/api/transaccion", tags=["Transaccion"])
app.include_router(routerFactura, prefix="/api/factura", tags=["Factura"])
app.include_router(routerServicios, prefix="/api/servicios", tags=["Servicios"])
app.include_router(routerInternal, prefix="/api/internal", tags=["Internal"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

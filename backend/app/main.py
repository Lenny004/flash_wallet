from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.factura import routerFactura
from app.api.routes.historial import routerHistorial
from app.api.routes.qr import routerQR
from app.api.routes.tarjeta import routerTarjeta
from app.api.routes.transaccion import routerTransaccion
from app.api.routes.usuarios import routerUsuario
from app.core.config import settings

# Crear una aplicación FastAPI
app = FastAPI()

# Configurar CORS desde variables de entorno
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Registrar los routers
app.include_router(routerUsuario, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(routerHistorial, prefix="/api/historial", tags=["Historial"])
app.include_router(routerTarjeta, prefix="/api/tarjeta", tags=["Tarjeta"])
app.include_router(routerQR, prefix="/api/decode_qr", tags=["QR"])
app.include_router(routerTransaccion, prefix="/api/transaccion", tags=["Transaccion"])
app.include_router(routerFactura, prefix="/api/factura", tags=["Factura"])

# Iniciar el servidor de desarrollo
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

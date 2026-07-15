# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.config import settings
from private.api_usuarios import routerUsuario
from private.api_historial import routerHistorial
from private.api_tarjeta import routerTarjeta
from private.api_qr import routerQR
from private.api_transaccion import routerTransaccion
from private.api_factura import routerFactura

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

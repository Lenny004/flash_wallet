from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.services.payments_worker import procesar_pagos_todas_tarjetas

routerInternal = APIRouter()


def verificar_internal_token(x_internal_token: str = Header(...)) -> None:
    if x_internal_token != settings.internal_api_token:
        raise HTTPException(status_code=403, detail="Token interno inválido")


@routerInternal.post("/procesar_pagos", dependencies=[Depends(verificar_internal_token)])
def procesar_pagos_interno(db: Session = Depends(get_db)):
    """
    Procesa pagos pendientes de todas las tarjetas (tarea batch/cron).
    Auth: requerida (header X-Internal-Token).
    """
    tarjetas_procesadas = procesar_pagos_todas_tarjetas(db)
    return {
        "estado": 1,
        "mensaje": "Pagos procesados correctamente.",
        "tarjetas_procesadas": tarjetas_procesadas,
    }

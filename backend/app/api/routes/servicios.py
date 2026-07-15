from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_U
from app.models.servicio import Servicio
from app.schemas.servicio_schema import ServicioOut, ServiciosListResponse

routerServicios = APIRouter()


@routerServicios.get("/", response_model=ServiciosListResponse)
def listar_servicios(
    datos_usuario=Depends(verificar_token_U),
    db: Session = Depends(get_db),
):
    """
    Lista todos los servicios disponibles para administración.
    Auth: requerida (token de usuario).
    """
    servicios_registrados = db.query(Servicio).order_by(Servicio.id_servicio).all()
    dataset = [
        ServicioOut(id=servicio.id_servicio, nombre=servicio.nombre, img_servicio=servicio.img_servicio)
        for servicio in servicios_registrados
    ]
    return {"estado": 1, "dataset": dataset}

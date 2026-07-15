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
    """Lista todos los servicios (admin). Requiere token de usuario."""
    servicios = db.query(Servicio).order_by(Servicio.id_servicio).all()
    dataset = [
        ServicioOut(id=s.id_servicio, nombre=s.nombre, img_servicio=s.img_servicio)
        for s in servicios
    ]
    return {"estado": 1, "dataset": dataset}

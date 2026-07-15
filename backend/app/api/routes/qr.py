from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.models.decode_qr import decode_qr_image
from app.models.servicio import Servicio
from app.services.qr_intent import crear_intent

routerQR = APIRouter()


@routerQR.post("/")
async def decode_qr(
    qr_image: UploadFile = File(...),
    datos_tarjeta=Depends(verificar_token_t),
    db: Session = Depends(get_db),
):
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")
    try:
        image_data = await qr_image.read()
        qr_text = decode_qr_image(image_data)

        if qr_text:
            qr_data = procesar_qr(qr_text, db)
            return qr_data
        else:
            raise HTTPException(status_code=404, detail="No se encontro un QR en la imagen brindada")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error de formato en el QR: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Interno: {str(e)}")


def procesar_qr(qr_text: str, db: Session):
    try:
        partes = qr_text.split("@")
        if len(partes) != 7:
            raise ValueError("Formato del QR no válido. No se ha encontrado un servicio válido")

        try:
            id_servicio = int(partes[0])
        except ValueError:
            raise HTTPException(status_code=400, detail="El ID de servicio no es válido")

        servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        data = {
            "id_servicio": id_servicio,
            "fecha": partes[1],
            "hora": partes[2],
            "monto": float(partes[3]),
            "frecuencia": int(partes[4]),
            "descripcion": partes[5],
            "id_estado": int(partes[6]),
        }
        intent = crear_intent(data)
        servicio_info = {
            "id_servicio": id_servicio,
            "nombre_servicio": servicio.nombre,
            "imagen": servicio.img_servicio,
        }
        return {
            "estado": 1,
            "intent": intent,
            "servicio": servicio_info,
            **servicio_info,
            **data,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error en el formato del QR: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando el QR: {str(e)}")

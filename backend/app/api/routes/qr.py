from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db, verificar_token_t
from app.core.rate_limit import rate_limit
from app.models.decode_qr import decode_qr_image
from app.models.servicio import Servicio
from app.services.qr_intent import crear_intent

routerQR = APIRouter()


@routerQR.post("/")
async def decode_qr(
    request: Request,
    qr_image: UploadFile = File(...),
    datos_tarjeta=Depends(verificar_token_t),
    db: Session = Depends(get_db),
):
    """
    Decodifica una imagen QR de pago, valida el servicio y devuelve un payment intent firmado.
    Auth: requerida (token de tarjeta).
    """
    if not datos_tarjeta:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

    id_tarjeta = datos_tarjeta.get("id_tarjeta")
    rate_limit(f"qr:{id_tarjeta}", limit=20, window=60)

    try:
        bytes_imagen = await qr_image.read()
        texto_qr = decode_qr_image(bytes_imagen)

        if texto_qr:
            resultado_qr = procesar_qr(texto_qr, db)
            return resultado_qr
        else:
            raise HTTPException(status_code=404, detail="No se encontro un QR en la imagen brindada")

    except ValueError as error_formato:
        raise HTTPException(status_code=400, detail=f"Error de formato en el QR: {str(error_formato)}")
    except HTTPException as error_http:
        raise error_http
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error Interno: {str(error)}")


def procesar_qr(texto_qr: str, db: Session):
    try:
        segmentos_qr = texto_qr.split("@")
        if len(segmentos_qr) != 7:
            raise ValueError("Formato del QR no válido. No se ha encontrado un servicio válido")

        try:
            id_servicio = int(segmentos_qr[0])
        except ValueError:
            raise HTTPException(status_code=400, detail="El ID de servicio no es válido")

        servicio_encontrado = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

        if not servicio_encontrado:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        datos_qr = {
            "id_servicio": id_servicio,
            "fecha": segmentos_qr[1],
            "hora": segmentos_qr[2],
            "monto": float(segmentos_qr[3]),
            "frecuencia": int(segmentos_qr[4]),
            "descripcion": segmentos_qr[5],
            "id_estado": int(segmentos_qr[6]),
        }
        intent_firmado = crear_intent(datos_qr)
        info_servicio = {
            "id_servicio": id_servicio,
            "nombre_servicio": servicio_encontrado.nombre,
            "imagen": servicio_encontrado.img_servicio,
        }
        return {
            "estado": 1,
            "intent": intent_firmado,
            "servicio": info_servicio,
            **info_servicio,
            **datos_qr,
        }

    except ValueError as error_formato:
        raise HTTPException(status_code=400, detail=f"Error en el formato del QR: {str(error_formato)}")
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Error procesando el QR: {str(error)}")

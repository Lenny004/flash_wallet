# api_qr.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from helpers.database import get_db
from models.decode_qr import decode_qr_image  # Importar la función de decodificación
from models.servicio import Servicio

routerQR = APIRouter()

@routerQR.post("/")
async def decode_qr(qr_image: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Leer la imagen
        image_data = await qr_image.read()

        # Llamar a la función decode_qr_image para decodificar el QR
        qr_text = decode_qr_image(image_data)

        if qr_text:
            # Procesar la cadena del QR, pasando la sesión `db`
            qr_data = procesar_qr(qr_text, db)
            return qr_data  # Retornar los valores procesados al frontend
        else:
            raise HTTPException(status_code=404, detail="No se encontro un QR en la imagen brindada")

    except ValueError as e:
        # Si ocurre un error de validación o formato, lo capturamos aquí
        raise HTTPException(status_code=400, detail=f"Error de formato en el QR: {str(e)}")
    except HTTPException as e:
        # Captura de HTTPException para no mezclar con el error interno
        raise e
    except Exception as e:
        # Si ocurre cualquier otro error no manejado, devolvemos un error genérico
        raise HTTPException(status_code=500, detail=f"Error Interno: {str(e)}")


def procesar_qr(qr_text: str, db: Session):
    try:
        partes = qr_text.split('@')
        if len(partes) != 7:
            raise ValueError("Formato del QR no válido. No se ha encontrado un servicio válido")

        # Validar que el ID de servicio es un entero
        try:
            id_servicio = int(partes[0])
        except ValueError:
            raise HTTPException(status_code=400, detail="El ID de servicio no es válido")

        # Buscar el servicio en la base de datos
        servicio = db.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()

        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        # Mapear los valores a un diccionario para retornar al frontend
        data = {
            "id_servicio": id_servicio,
            "nombre_servicio": servicio.nombre,
            "imagen": servicio.img_servicio,
            "fecha": partes[1],
            "hora": partes[2],
            "monto": float(partes[3]),  # Convertir el monto a flotante
            "frecuencia": int(partes[4]),  # Convertir la frecuencia a entero
            "descripcion": partes[5],
            "id_estado": int(partes[6])  # Convertir el ID del estado a entero
        }
        return data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error en el formato del QR: {str(e)}")
    except Exception as e:
        # Capturar cualquier excepción que ocurra durante el procesamiento del QR
        raise HTTPException(status_code=400, detail=f"Error procesando el QR: {str(e)}")

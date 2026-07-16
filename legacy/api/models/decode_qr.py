from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO

def decode_qr_image(image_data: bytes) -> str:
    try:
        # Abrir la imagen desde los datos en bytes
        img = Image.open(BytesIO(image_data))
        
        # Decodificar el código QR
        qr_data = decode(img)
        
        if qr_data:
            return qr_data[0].data.decode('utf-8')  # Devolver el texto decodificado
        else:
            return None  # Si no se encuentra un código QR
    except Exception as e:
        raise ValueError(f"Error decoding QR: {e}")

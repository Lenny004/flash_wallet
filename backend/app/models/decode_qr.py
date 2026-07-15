from io import BytesIO

from PIL import Image
from pyzbar.pyzbar import decode


def decode_qr_image(image_data: bytes) -> str:
    try:
        # Abrir la imagen desde los datos en bytes
        img = Image.open(BytesIO(image_data))

        # Decodificar el código QR
        qr_data = decode(img)

        if qr_data:
            return qr_data[0].data.decode("utf-8")
        else:
            return None
    except Exception as e:
        raise ValueError(f"Error decoding QR: {e}")

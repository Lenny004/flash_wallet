const API_DECODE = window.FLASH_API_BASE + '/api/decode_qr/';
const API_TRANSACCION = window.FLASH_API_BASE + '/api/transaccion/';
const token_tarjeta = localStorage.getItem('token_tarjeta');

let qrIntent = null;

// Mostrar y procesar imagen del QR
function mostrarImagen(event) {
    vaciarCampos();
    const fileInput = event.target;
    const qrImage = document.getElementById('qrImage');

    if (fileInput.files && fileInput.files[0]) {
        const file = fileInput.files[0];

        // Validar que sea una imagen
        if (!file.type.startsWith('image/')) {
            sweetAlert(4, "Selecciona un archivo de imagen válido.");
            fileInput.value = '';
            return;
        }

        // Leer la imagen y mostrarla
        const reader = new FileReader();
        reader.onload = (e) => {
            qrImage.src = e.target.result;
            qrImage.style.display = 'block';
        };
        reader.readAsDataURL(file);

        // Crear FormData para enviar la imagen
        const formData = new FormData();
        formData.append('qr_image', file);

        // Decodificar el QR
        fetch(API_DECODE, {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.detail || "Error desconocido");
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.estado === 1 || data.id_servicio) {
                    qrIntent = data.intent || null;
                    const servicio = data.servicio || data;
                    let content = `
                        <img src="../api/images/servicios/${servicio.imagen}" alt="empresa">
                        <div class="caja borde"><p>${servicio.nombre_servicio}</p></div>
                        <div class="caja borde"><p>${data.descripcion}</p></div>
                        <div class="caja borde"><p>Costo: ${data.monto}</p></div>`;
                    document.getElementById('fecha_transaccion').value = data.fecha;
                    document.getElementById('hora_transaccion').value = data.hora;
                    document.getElementById('monto').value = data.monto;
                    document.getElementById('frecuencia').value = data.frecuencia;
                    document.getElementById('descripcion').value = data.descripcion;
                    document.getElementById('id_servicio').value = data.id_servicio;
                    document.getElementById('id_estado').value = data.id_estado;
                    document.getElementById('info_servicio').innerHTML = content;
                } else {
                    sweetAlert(2, data.error);
                }
            })
            .catch(error => {
                sweetAlert(2, `Error: ${error.message}`);
            });
    }
}

// Enviar formulario
document.getElementById('factura_form').addEventListener('submit', function (event) {
    event.preventDefault();
    if (!token_tarjeta) {
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    if (!qrIntent || !qrIntent.sig || !qrIntent.exp) {
        sweetAlert(4, "Escanea un QR válido antes de crear la transacción.", null);
        return;
    }

    const fechaTransaccion = qrIntent.fecha.replace(/\//g, '-');
    const bodyData = {
        fecha_transaccion: fechaTransaccion,
        hora_transaccion: qrIntent.hora,
        monto: qrIntent.monto,
        frecuencia: qrIntent.frecuencia,
        descripcion: qrIntent.descripcion,
        id_servicio: qrIntent.id_servicio,
        id_estado: qrIntent.id_estado,
        exp: qrIntent.exp,
        sig: qrIntent.sig
    };

    fetch(API_TRANSACCION + 'crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`
        },
        body: JSON.stringify(bodyData)
    }).then(request => {
            if (request.ok) {
                return request.json();
            } else {
                return request.json().then(data => {
                    throw new Error(data.detail || request.statusText);
                });
            }
        })
        .then(response => {
            if (response.estado === 1) {
                sweetAlert(1, response.mensaje);
                vaciarCampos();
            } else {
                sweetAlert(4, response.exception || "Error desconocido", null);
            }
        })
        .catch(error => {
            sweetAlert(4, error.message || 'Hubo un problema con la solicitud.', null);
            console.log('Error:', error);
        });
});

// Vaciar campos
function vaciarCampos() {
    qrIntent = null;
    document.getElementById('fecha_transaccion').value = "";
    document.getElementById('hora_transaccion').value = "";
    document.getElementById('monto').value = "";
    document.getElementById('frecuencia').value = "";
    document.getElementById('descripcion').value = "";
    document.getElementById('id_servicio').value = "";
    document.getElementById('id_estado').value = "";
    let content = `
        <img src="../resources/imgs/default.jpg" alt="empresa">
        <div class="caja borde"><p></p></div>
        <div class="caja borde"><p></p></div>
        <div class="caja borde"><p>Costo: </p></div>`;
    document.getElementById('info_servicio').innerHTML = content;
}

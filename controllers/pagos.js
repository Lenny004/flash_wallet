const API_TRANSACCION = window.FLASH_API_BASE + '/api/transaccion/';
const token_tarjeta = localStorage.getItem('token_tarjeta');

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    const token_usuario = localStorage.getItem('token_usuario'); 
    if (!token_usuario) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay sesión activa. Redirigiendo al login...", "login.html");
        return;
    }
    readRows(API_TRANSACCION + 'read');
});

function readRows(api) {
    if (!token_tarjeta) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay datos de la tarjeta.", null);
        return;
    }
    fetch(api, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`
        }
    }).then(function (request) {
        if (request.ok) {
            request.json().then(function (response) {
                if (response.estado === 1) {
                    fillTable(response.dataset);
                } else {
                    sweetAlert(4, "Error en la respuesta: " + response.exception, null);
                }
            });
        } else {
            sweetAlert(2, request.statusText, null);
        }
    }).catch(function (error) {
        sweetAlert(4, 'Hubo un problema con la solicitud.', null);
    });
}

// Función para llenar la tabla con los datos de los registros. Se manda a llamar en la función readRows().
function fillTable(dataset) {
    let content = [];
    // Se recorre el conjunto de registros (dataset)
    dataset.forEach(function (row) {
        if (row.id_estado == 1) {
            content.push(
            `<div class="tarjeta_servicio">
                <div class="datos_servicio">
                    <hr class="estado_p">
                    <h2>${row.nombre}</h2>
                    <p>${row.descripcion}</p>
                    <p>Fecha: ${row.fecha_transaccion} ${row.hora_transaccion} PM</p>
                    <p>Monto: ${row.monto}</p>
                </div>
                <div class="estado_servicio">
                    <p class="estado_p"><b>${row.estado}</b></p>
                </div>
            </div>`);
        } else {
            content.push(
            `<div class="tarjeta_servicio">
                <div class="datos_servicio">
                    <hr class="estado_e">
                    <h2>${row.nombre}</h2>
                    <p>${row.descripcion}</p>
                    <p>Fecha: ${row.fecha_transaccion} ${row.hora_transaccion}</p>
                    <p>Monto: ${row.monto}</p>
                </div>
                <div class="estado_servicio">
                    <p class="estado_e"><b>${row.estado}</b></p>
                </div>
            </div>`);
        }
    });
    // Se agregan las filas al cuerpo de la tabla
    document.getElementById('tarjetas_pago').innerHTML = content.join('');
}
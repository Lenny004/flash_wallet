// Constante para establecer la ruta y parámetros de comunicación con la API en Flask.
const API_HISTORIAL = window.FLASH_API_BASE + '/api/historial/';
const API_TARJETA = window.FLASH_API_BASE + '/api/tarjeta/';
const API_MOVIMIENTOS = window.FLASH_API_BASE + '/api/historial/movimientos';

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    readRows(API_HISTORIAL + 'read');
    datosTarjeta();
    loadMovimientos();
});

/*
*   Función para obtener todos los registros disponibles en los mantenimientos de tablas (operación read).
*   Parámetros: api (ruta del servidor para obtener los datos).
*   Retorno: ninguno.
*/
function readRows(api) {
    if (!localStorage.getItem('token_tarjeta')) {
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    apiFetchAuth(api, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    }).then(function (request) {
        if (request.ok) {
            request.json().then(function (response) {
                if (response.estado === 1) {
                    fillTable(response.dataset);
                }
            });
        } else {
            sweetAlert(2, request.statusText);
        }
    }).catch(function (error) {
        sweetAlert(4, 'Hubo un problema con la solicitud.', null);
        console.log('Error:', error);
    });
}

document.getElementById('buscador-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const monto_agregado = document.getElementById('buscar').value;
    apiFetchAuth(API_HISTORIAL + 'buscar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ monto_agregado })
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then((errorData) => {
                throw new Error(errorData.detail || 'Error desconocido');
            });
        }
    })
    .then((data) => {
        if (data.estado) {
            fillTable(data.dataset);
            sweetAlert(1, data.mensaje, null);
        } else {
            sweetAlert(4, data.exception || 'No hay resultados', null);
            readRows(API_HISTORIAL + 'read');
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null);
        console.log(error);
        readRows(API_HISTORIAL + 'read');
    });
});


// Función para llenar la tabla con los datos de los registros. Se manda a llamar en la función readRows().
function fillTable(dataset) {
    let content = [];
    dataset.forEach(function (row) {
        content.push(`
            <tr>
                <td>$${row.monto_agregado}</td>
                <td>${row.fecha_historial}</td>
                <td>${row.hora_historial}</td>
                <td>
                    <img onclick="openDelete(${row.id_historial})" src="../resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
    });
    document.getElementById('tbhistorial').innerHTML = content.join('');
}

function loadMovimientos() {
    const aviso = document.getElementById('movimientos-aviso');
    const tbody = document.getElementById('tbmovimientos');
    if (!localStorage.getItem('token_tarjeta')) {
        if (aviso) {
            aviso.hidden = false;
            aviso.textContent = 'No se pudieron cargar los movimientos.';
        }
        return;
    }
    apiFetchAuth(API_MOVIMIENTOS, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function (request) {
        if (request.ok) {
            return request.json();
        }
        throw new Error(request.statusText);
    })
    .then(function (response) {
        if (response.estado === 1) {
            fillMovimientosTable(response.dataset);
        } else {
            throw new Error(response.exception || 'No se pudieron cargar los movimientos.');
        }
    })
    .catch(function (error) {
        console.log('Movimientos:', error);
        if (aviso) {
            aviso.hidden = false;
            aviso.textContent = 'No se pudieron cargar los movimientos.';
        }
        if (tbody) {
            tbody.innerHTML = '';
        }
    });
}

function formatFechaMovimiento(creadoEn) {
    const fecha = new Date(creadoEn);
    if (isNaN(fecha.getTime())) {
        return creadoEn || '-';
    }
    return fecha.toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatMontoMovimiento(valor) {
    return '$' + parseFloat(valor).toFixed(2);
}

function fillMovimientosTable(dataset) {
    const tbody = document.getElementById('tbmovimientos');
    if (!tbody) {
        return;
    }
    if (!dataset || dataset.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No hay movimientos registrados.</td></tr>';
        return;
    }
    let content = [];
    dataset.forEach(function (row) {
        content.push(`
            <tr>
                <td>${formatFechaMovimiento(row.creado_en)}</td>
                <td>${row.tipo}</td>
                <td>${formatMontoMovimiento(row.monto)}</td>
                <td>${formatMontoMovimiento(row.saldo_anterior)}</td>
                <td>${formatMontoMovimiento(row.saldo_nuevo)}</td>
                <td>${row.referencia || '-'}</td>
            </tr>
        `);
    });
    tbody.innerHTML = content.join('');
}

function datosTarjeta() {
    if (!localStorage.getItem('token_tarjeta')) {
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    apiFetchAuth(API_TARJETA + "readOne", {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then((request) => {
        if (request.ok) {
            return request.json();
        } else {
            return request.json().then((error) => {
                console.error('Error en la solicitud:', error);
                throw new Error(error.detail || "Error al cargar los datos.");
            });
        }
    })
    .then((response) => {
        if (response.estado) {
            let content, content2 = "";
            content = `
                <p><b>${response.pan}</b></p>
                <p><b>DESDE: ${response.fecha_creacion}</b></p>
                <p><b>CVC: ${response.cvc}</b></p>
                <p><b>${response.nombre}</b></p>`;
            document.getElementById('datos_tarjeta').innerHTML = content;
            content2 =
            `<p>Saldo en tu wallet</p>
            <p>$${parseFloat(response.balance).toFixed(2)}</p>`;
            document.getElementById('dato_balance').innerHTML = content2;
        } else {
            sweetAlert(3, response.exception || 'Ocurrió un error.', null);
        }
    })
    .catch((error) => {
        console.error('Error:', error.message);
        sweetAlert(3, error.message, "login.html");
    });
}


function openDelete(id){
    let id_historial = id;
    Swal.fire({
        title: 'Advertencia',
        text: '¿Desea eliminar el registro?',
        icon: 'warning',
        confirmButtonText: 'Si',
        confirmButtonColor: '#b01e68',
        showCancelButton: true,
        cancelButtonColor: '#6b4a5f',
        cancelButtonText: 'No',
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: true,
        stopKeydownPropagation: false
    }).then((result) => {
        if (result.isConfirmed) {
            apiFetchAuth(API_HISTORIAL + "delete", {
                method: 'post',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_historial }),
            }).then(function (request) {
                if (request.ok) {
                    request.json().then(function (response) {
                        if (response.estado) {
                            readRows(API_HISTORIAL + 'read');
                            sweetAlert(1, response.message, null);
                        } else {
                            readRows(API_HISTORIAL + 'read');
                            sweetAlert(2, response.exception, null);
                        }
                    });
                } else {
                    console.log(request.estado + ' ' + request.estadoText);
                }
            });
        }
    });
}

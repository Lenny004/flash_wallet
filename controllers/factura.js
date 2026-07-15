const API_FACTURA = window.FLASH_API_BASE + '/api/factura/';

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    readRows(API_FACTURA + 'read');
});

function readRows(api) {
    if (!localStorage.getItem('token_tarjeta')) {
        sweetAlert(3, "No hay datos de la tarjeta.", null);
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
            sweetAlert(2, request.statusText, null);
        }
    }).catch(function (error) {
        sweetAlert(4, 'Hubo un problema con la solicitud.', null);
    });
}


// Función para llenar la tabla con los datos de los registros. Se manda a llamar en la función readRows().
function fillTable(dataset) {
    let content = [];
    dataset.forEach(function (row) {
        content.push(`
            <tr>
                <td>${row.nombre_servicio}</td>
                <td>${row.fecha_factura}</td>
                <td>${row.hora_factura}</td>
                <td>$${row.monto_total}</td>
                <td>
                    <img onclick="openDelete(${row.id_factura})" src="../resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
    });
    document.getElementById('tbfactura').innerHTML = content.join('');
}

document.getElementById('buscador-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const nombre = document.getElementById('buscar').value;
    apiFetchAuth(API_FACTURA + 'buscar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre })
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
            readRows(API_FACTURA + 'read');
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null);
        console.log(error);
        readRows(API_FACTURA + 'read');
    });
});


function openDelete(id){
    let id_factura = id;
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
            apiFetchAuth(API_FACTURA + "delete", {
                method: 'post',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_factura }),
            }).then(function (request) {
                if (request.ok) {
                    request.json().then(function (response) {
                        if (response.estado) {
                            readRows(API_FACTURA + 'read');
                            sweetAlert(1, response.message, null);
                        } else {
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

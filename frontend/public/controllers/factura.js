const API_FACTURA = window.FLASH_API_BASE + '/api/factura/';
const token_tarjeta = localStorage.getItem('token_tarjeta');

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    readRows(API_FACTURA + 'read');
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
                    //sweetAlert(4, "Error en la respuesta: " + response.exception, null);
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
        // Se crean y concatenan las filas de la tabla con los datos de cada registro
        content.push(`
            <tr>
                <td>${row.nombre_servicio}</td>
                <td>${row.fecha_factura}</td>
                <td>${row.hora_factura}</td>
                <td>$${row.monto_total}</td>
                <td>
                    <!--Boton Eliminar-->
                    <img onclick="openDelete(${row.id_factura})" src="../resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
    });
    // Se agregan las filas al cuerpo de la tabla
    document.getElementById('tbfactura').innerHTML = content.join('');
}

document.getElementById('buscador-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Evita la recarga de la página
    // Obtener los valores del formulario
    const nombre = document.getElementById('buscar').value;
    fetch(API_FACTURA + 'buscar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token_tarjeta}`},
        body: JSON.stringify({nombre})  // Enviamos los datos del formulario como JSON
    })
    .then((response) => {
        if (response.ok) {
            return response.json(); // Si la respuesta es exitosa, parsea el JSON
        } else {
            // Si no la respuesta no es exitosa, lanza un error
            return response.json().then((errorData) => {
                throw new Error(errorData.detail || 'Error desconocido');
            });
        }
    })
    .then((data) => {
        if (data.estado) { // Aquí se usa "response" correctamente
            fillTable(data.dataset); // Llenamos la tabla con los resultados
            sweetAlert(1, data.mensaje, null); // Mostramos mensaje de éxito
        } else {
            sweetAlert(4, data.exception || 'No hay resultados', null); // Si no hay resultados
            readRows(API_FACTURA + 'read');
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null); // Muestra el mensaje de error
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
            fetch(API_FACTURA + "delete", {
                method: 'post',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id_factura}),
            }).then(function (request) {
                // Se verifica si la petición es correcta, de lo contrario se muestra un mensaje en la consola indicando el problema.
                if (request.ok) {
                    // Se obtiene la respuesta en formato JSON.
                    request.json().then(function (response) {
                        // Se comprueba si la respuesta es satisfactoria, de lo contrario se muestra un mensaje con la excepción.
                        if (response.estado) {
                            readRows(API_FACTURA + 'read');
                            // Se cargan nuevamente las filas en la tabla de la vista después de borrar un registro y se muestra un mensaje de éxito.
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
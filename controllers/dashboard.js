// Constante para establecer la ruta y parámetros de comunicación con la API en Flask.
const API_HISTORIAL = 'http://127.0.0.1:8000/api/historial/'; // Cambia según la ruta de tu servidor FastAPI
const API_TARJETA = 'http://127.0.0.1:8000/api/tarjeta/';
const token_tarjeta = localStorage.getItem('token_tarjeta');  // Obtener el token almacenado

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    readRows(API_HISTORIAL + 'read');
    datosTarjeta();
});

/*
*   Función para obtener todos los registros disponibles en los mantenimientos de tablas (operación read).
*   Parámetros: api (ruta del servidor para obtener los datos).
*   Retorno: ninguno.
*/
function readRows(api) {
    if (!token_tarjeta) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    fetch(api, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`  // Asegúrate de que el token esté siendo enviado correctamente
        }
    }).then(function (request) {
        // Se verifica si la petición es correcta
        if (request.ok) {
            // Se obtiene la respuesta en formato JSON
            request.json().then(function (response) {
                // Se comprueba si la respuesta es satisfactoria para obtener los datos
                if (response.estado === 1) {
                    fillTable(response.dataset);
                } else {
                    //sweetAlert(4, response.exception, null); // Si la respuesta es estado 0, muestra el mensaje de error
                }
            });
        } else {
            sweetAlert(2, request.statusText); // Muestra el error si no se puede procesar la solicitud
        }
    }).catch(function (error) {
        sweetAlert(4, 'Hubo un problema con la solicitud.', null);
        console.log('Error:', error);
    });
}

document.getElementById('buscador-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Evita la recarga de la página
    // Obtener los valores del formulario
    const monto_agregado = document.getElementById('buscar').value;
    fetch(API_HISTORIAL + 'buscar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${token_tarjeta}`},
        body: JSON.stringify({monto_agregado})  // Enviamos los datos del formulario como JSON
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
            readRows(API_HISTORIAL + 'read');
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null); // Muestra el mensaje de error
        console.log(error);
        readRows(API_HISTORIAL + 'read');
    });
});


// Función para llenar la tabla con los datos de los registros. Se manda a llamar en la función readRows().
function fillTable(dataset) {
    let content = [];
    // Se recorre el conjunto de registros (dataset)
    dataset.forEach(function (row) {
        // Se crean y concatenan las filas de la tabla con los datos de cada registro
        content.push(`
            <tr>
                <td>$${row.monto_agregado}</td>
                <td>${row.fecha_historial}</td>
                <td>${row.hora_historial}</td>
                <td>
                    <!--Boton Eliminar-->
                    <img onclick="openDelete(${row.id_historial})" src="../resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
    });
    // Se agregan las filas al cuerpo de la tabla
    document.getElementById('tbhistorial').innerHTML = content.join('');
}

function datosTarjeta() {
    if (!token_tarjeta) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    // Llamada a la API para obtener los datos del usuario
    fetch(API_TARJETA + "readOne", {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`  // Asegúrate de que el token esté siendo enviado correctamente
        }
    })
    .then((request) => {
        // Verificar si la solicitud fue exitosa
        if (request.ok) {
            return request.json();  // Convertir la respuesta en JSON
        } else {
            return request.json().then((error) => {
                console.error('Error en la solicitud:', error);  // Ver el error detallado
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
            // Se agrega al bloque de tarjeta
            document.getElementById('datos_tarjeta').innerHTML = content;
            content2 = 
            `<p>Saldo en tu wallet</p>
            <p>$${parseFloat(response.balance).toFixed(2)}</p>`;
            document.getElementById('dato_balance').innerHTML = content2;
        } else {
            // Si la respuesta contiene un error, mostrar un mensaje
            sweetAlert(3, response.exception || 'Ocurrió un error.', null);
        }
    })
    .catch((error) => {
        // Capturar y mostrar cualquier error ocurrido en la llamada
        console.error('Error:', error.message);
        sweetAlert(3, error.message, "login.html");  // Redirigir al login en caso de error
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
            fetch(API_HISTORIAL + "delete", {
                method: 'post',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({id_historial}),
            }).then(function (request) {
                // Se verifica si la petición es correcta, de lo contrario se muestra un mensaje en la consola indicando el problema.
                if (request.ok) {
                    // Se obtiene la respuesta en formato JSON.
                    request.json().then(function (response) {
                        // Se comprueba si la respuesta es satisfactoria, de lo contrario se muestra un mensaje con la excepción.
                        if (response.estado) {
                            readRows(API_HISTORIAL + 'read');
                            // Se cargan nuevamente las filas en la tabla de la vista después de borrar un registro y se muestra un mensaje de éxito.
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
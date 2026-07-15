const API_HISTORIAL = 'http://127.0.0.1:8000/api/historial/';
const API_TRANSACCION = 'http://127.0.0.1:8000/api/transaccion/';

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    obtenerMonto();
});

document.getElementById('recarga_form').addEventListener('submit', function (event) {
    event.preventDefault();
    const token_tarjeta = localStorage.getItem('token_tarjeta');  // Obtener el token almacenado
    if (!token_tarjeta) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    fetch(API_HISTORIAL + 'recargar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`
        },
        body: JSON.stringify(Object.fromEntries(new FormData(event.target))) // Enviamos los datos del formulario como JSON
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
            sweetAlert(1, data.mensaje, null); // Mostramos mensaje de éxito
        } else {
            sweetAlert(4, data.exception || 'No hay resultados', null); // Si no hay resultados
        }
    })
    .catch((error) => {
        if (error.message.includes("401")) {
            sweetAlert(3, "Sesión expirada. Inicia sesión nuevamente.", null);
        } else if (error.message.includes("404")) {
            sweetAlert(3, "Tarjeta no encontrada.", null);
        } else {
            sweetAlert(4, error.message, null);
        }
    });
});


const cancelButton = document.querySelector('cancel');
cancelButton.addEventListener('click', function () {
    alert('Operación cancelada.');
});


function obtenerMonto(){
    const token_tarjeta = localStorage.getItem('token_tarjeta');  // Obtener el token almacenado
    if (!token_tarjeta) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }

    // Función para obtener el monto pendiente
    fetch(API_TRANSACCION + 'saldo_pendiente', {
        method: 'GET',
        headers:{'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_tarjeta}`
        },
    })
    .then((response) => {
        if (response.ok) {
            return response.json();  // Si la respuesta es exitosa, parsea el JSON
        } else {
            // Si no la respuesta no es exitosa, lanza un error
            return response.json().then((errorData) => {
                throw new Error(errorData.detail || 'Error desconocido al obtener saldo pendiente');
            });
        }
    })
    .then((data) => {
        if (data.estado) {
            // Mostrar el monto pendiente en el frontend
            const montoPendiente = data.monto_pendiente;
            document.getElementById('minima').value = "Cantidad minima a recargar: $" + montoPendiente.toFixed(2);
        } else {
            sweetAlert(4, data.mensaje || 'No se pudo obtener el saldo pendiente', null);  // En caso de error al obtener el monto pendiente
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null);
    });
}

const API_HISTORIAL = window.FLASH_API_BASE + '/api/historial/';
const API_TRANSACCION = window.FLASH_API_BASE + '/api/transaccion/';

//Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    obtenerMonto();
});

document.getElementById('recarga_form').addEventListener('submit', function (event) {
    event.preventDefault();
    if (!localStorage.getItem('token_tarjeta')) {
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }
    apiFetchAuth(API_HISTORIAL + 'recargar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(event.target)))
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
            sweetAlert(1, data.mensaje, null);
        } else {
            sweetAlert(4, data.exception || 'No hay resultados', null);
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
    if (!localStorage.getItem('token_tarjeta')) {
        sweetAlert(3, "No hay datos de la tarjeta. Error", null);
        return;
    }

    apiFetchAuth(API_TRANSACCION + 'saldo_pendiente', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then((response) => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then((errorData) => {
                throw new Error(errorData.detail || 'Error desconocido al obtener saldo pendiente');
            });
        }
    })
    .then((data) => {
        if (data.estado) {
            const montoPendiente = data.monto_pendiente;
            document.getElementById('minima').value = "Cantidad minima a recargar: $" + montoPendiente.toFixed(2);
        } else {
            sweetAlert(4, data.mensaje || 'No se pudo obtener el saldo pendiente', null);
        }
    })
    .catch((error) => {
        sweetAlert(4, error.message, null);
    });
}

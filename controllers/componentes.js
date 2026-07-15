// Asignar validaciones a los inputs correspondientes
document.addEventListener('DOMContentLoaded', () => {
    // Número de tarjeta: solo números y formato con guiones
    const numeroTarjetaInput = document.getElementById('numero_t');
    numeroTarjetaInput.addEventListener('input', formatearNumeroTarjeta);

    // CVC: solo números y máximo 4 dígitos
    const cvcInput = document.getElementById('cvc');
    cvcInput.addEventListener('input', validarCVC);

    // Nombre titular: solo letras y espacios
    const nombreTitularInput = document.getElementById('nombre_titular');
    nombreTitularInput.addEventListener('keypress', permitirSoloLetras);

    // Monto: solo números
    const montoInput = document.getElementById('monto_agregado');
    montoInput.addEventListener('input', permitirSoloNumeros);
});

// Validar solo letras para nombres y apellidos
function permitirSoloLetras(event) {
    const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$/;
    if (!regex.test(event.key)) {
        event.preventDefault();
    }
}

// Formatear automáticamente el número de tarjeta (agrega guion cada 4 dígitos)
function formatearNumeroTarjeta(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, ''); // Elimina cualquier carácter no numérico
    let formattedValue = '';
    for (let i = 0; i < value.length; i += 4) {
        formattedValue += value.substr(i, 4) + (i + 4 < value.length ? '-' : '');
    }
    input.value = formattedValue; // Actualiza el valor del input formateado
}

// Validar que el CVC tenga solo 3 o 4 dígitos
function validarCVC(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, ''); // Elimina caracteres no numéricos

    // Limitar a 4 dígitos como máximo
    if (value.length > 4) {
        value = value.slice(0, 4); // Recorta el valor si tiene más de 4 dígitos
    }

    // Establecer el valor del campo
    input.value = value;

    if (value.length === 3 || value.length === 4) {
        input.setCustomValidity(""); // Si tiene 3 o 4 dígitos, el valor es válido
    } else {
        input.setCustomValidity("El CVC debe ser de 3 o 4 dígitos.");
    }
}

// Validar que solo se ingresen números
function permitirSoloNumeros(event) {
    if (event.key < '0' || event.key > '9') {
        event.preventDefault(); // Bloquea cualquier carácter que no sea un número
    }
}


// Validar entrada de teléfono para permitir solo números, espacios y '+'
const telefonoInput = document.getElementById('telefono');
telefonoInput.addEventListener('keypress', (event) => {
    const regex = /^[0-9+\s]*$/; // Solo números, '+' y espacios
    if (!regex.test(event.key)) {
        event.preventDefault(); // Bloquear caracteres inválidos
    }
});

// Validar que el teléfono no contenga letras ni caracteres inválidos en el pegado
telefonoInput.addEventListener('input', () => {
    telefonoInput.value = telefonoInput.value.replace(/[^0-9+\s]/g, ''); // Reemplazar caracteres inválidos
});


// Nombre titular: solo letras y espacios
const direccioninput = document.getElementById('direccion');
direccioninput.addEventListener('keypress', (event) => {
    const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\^0-9\s\,\.]*$/;
    if (!regex.test(event.key)) {
        event.preventDefault();
    }
});

// Validar que el teléfono no contenga letras ni caracteres inválidos en el pegado
direccioninput.addEventListener('input', () => {
    direccioninput.value = direccioninput.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\^0-9\s\,\.]/g, ''); // Reemplazar caracteres inválidos
});


// Habilitar edición de campos
function habilitarEdit() {
    document.getElementById('nombres').disabled = false;
    document.getElementById('apellidos').disabled = false;
    document.getElementById('email').disabled = false;
    document.getElementById('direccion').disabled = false;
    document.getElementById('telefono').disabled = false;
}

/*
*   Función para manejar los mensajes de notificación al usuario. Requiere el archivo sweetalert.min.js para funcionar.
*   Parámetros: type (tipo de mensaje), text (texto a mostrar) y url (ubicación para enviar al cerrar el mensaje).
*   Retorno: ninguno.
*/
function sweetAlert(type, text, url) {
    // Se compara el tipo de mensaje a mostrar.
    switch (type) {
        case 1:
            title = 'Éxito';
            icon = 'success';
            break;
        case 2:
            title = 'Error';
            icon = 'error';
            break;
        case 3:
            title = 'Advertencia';
            icon = 'warning';
            break;
        case 4:
            title = 'Aviso';
            icon = 'info';
            break;
        case 5:
            title = 'Campos Vacios';
            icon = 'warning';
            break;
    }
    // Si existe una ruta definida, se muestra el mensaje y se direcciona a dicha ubicación, de lo contrario solo se muestra el mensaje.
    if (url) {
        Swal.fire({
            title: title,
            text: text,
            icon: icon,
            confirmButtonText: 'Aceptar',
            allowOutsideClick: false,
            allowEscapeKey: false,
            allowEnterKey: true,
            stopKeydownPropagation: false
        }).then(function () {
            location.href = url
        });
    } else {
        Swal.fire({
            toast: true,
            position: 'bottom-end',
            timer: 5000,
            timerProgressBar: true,
            title: title,
            text: text,
            icon: icon,
            color: '#9e2d2d',
            background: '#fffff',
            customClass: {
                popup: 'custom-swal-popup' // Clase personalizada para más estilos
            },
            showConfirmButton: false,
            stopKeydownPropagation: false
        });
    }
}

function logOut() {
    Swal.fire({
        title: 'Cerrar Sesión',
        text: '¿Está seguro de cerrar la sesión?',
        color: '#9E2D2D',
        confirmButtonText: 'Sí',
        confirmButtonColor: '#9E2D2D',
        showCancelButton: true,
        cancelButtonColor: '#b3b3b3',
        cancelButtonText: 'No',
        allowOutsideClick: false,
        allowEscapeKey: false,
        allowEnterKey: true,
        stopKeydownPropagation: false
    }).then((result) => {
        if (result.isConfirmed) {
            // Eliminar los tokens almacenados en el navegador
            localStorage.removeItem('token_usuario');
            localStorage.removeItem('token_tarjeta');
            localStorage.removeItem('refresh_token');

            // Mostrar mensaje de confirmación y redirigir al usuario
            sweetAlert(1, 'Sesión cerrada correctamente', 'login.html');
        } else {
            sweetAlert(4, 'Puede continuar con la sesión', null);
        }
    });
}

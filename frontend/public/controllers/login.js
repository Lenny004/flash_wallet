// Constante para establecer la ruta y parámetros de comunicación con la API en Flask.
const API_LOGIN = window.FLASH_API_BASE + '/api/usuarios/';

document.addEventListener('DOMContentLoaded', function () {
    // Petición para consultar si existen usuarios registrados.
    fetch(API_LOGIN, {
        method: 'GET',
    }).then((request) => {
        if (request.ok) {
            request.json().then((response) => {
                // Comprobar si existe una sesión activa.
                if (response.session) {
                    location.href = 'dashboard.html';
                } else if (response.hay_usuarios === false || response.estado === 0) {
                    sweetAlert(3, response.exception || 'No hay usuarios registrados.', 'registro.html');
                } else {
                    Swal.fire({
                        title: 'Bienvenido a Flash',
                        text: 'Ya puede ingresar al sistema',
                        imageUrl: '../resources/imgs/Flash_logo.png',
                        imageWidth: 80,
                        imageHeight: 80,
                        imageAlt: 'Custom image',
                        confirmButtonText: 'Continuar',
                        allowOutsideClick: false,
                        allowEscapeKey: false,
                        allowEnterKey: true,
                        stopKeydownPropagation: false,
                    });
                }
            });
        } else {
            sweetAlert(3, request.detail);
        }
    }).catch((error) => {
        console.error('Error en la petición:', error);
    });
});

//Enviar los datos de las credenciales
document.getElementById('login_form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevenir el recargado de página
    // Obtener los valores del formulario
    const usuario = document.getElementById('usuario').value;
    const contra = document.getElementById('contra').value;
    // Hacer la petición al servidor
    fetch(API_LOGIN + 'login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario, contra }),  
    })
    .then((response) => {
        return response.json().then((data) => {
            if (!response.ok) {
                // Si el servidor devuelve un error, mostramos el mensaje
                throw new Error(data.detail || "Error desconocido");
            }
            return data;
        });
    })
    .then((data) => {
        // Guardar el token en localStorage
        if (data.token_usuario && data.token_tarjeta) {
            localStorage.setItem('token_usuario', data.token_usuario);
            localStorage.setItem('token_tarjeta', data.token_tarjeta);
            if (data.refresh_token) {
                localStorage.setItem('refresh_token', data.refresh_token);
            }
            sweetAlert(1, data.mensaje, "dashboard.html");
        } else {
            sweetAlert(2, "No se recibió un token válido del servidor.");
        }
    })
    .catch((error) => {
        sweetAlert(2, error.message);  // Muestra el mensaje correcto
    });
});


document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordField = document.getElementById('contra');
    const passwordToggle = this.querySelector('img');

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        passwordToggle.src = '../resources/icons/ver.png'; // Cambia a un ícono diferente
    } else {
        passwordField.type = 'password';
        passwordToggle.src = '../resources/icons/ocultar.png';
    }
});
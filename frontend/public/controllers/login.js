// Constante para establecer la ruta y parámetros de comunicación con la API.
const API_LOGIN = window.FLASH_API_BASE + '/api/usuarios/';

function mensajeDesdeDetail(detail, fallback) {
    if (typeof detail === 'string' && detail.trim() !== '') return detail;
    if (Array.isArray(detail)) {
        const partes = detail.map((item) => {
            if (typeof item === 'string') return item;
            if (item && typeof item === 'object' && item.msg) return String(item.msg);
            return '';
        }).filter(Boolean);
        if (partes.length) return partes.join(' ');
    }
    return fallback || 'Error desconocido';
}

document.addEventListener('DOMContentLoaded', function () {
    fetch(API_LOGIN, { method: 'GET' })
        .then((request) => {
            if (request.ok) {
                return request.json().then((response) => {
                    if (response.session) {
                        location.href = 'dashboard.html';
                    } else if (response.hay_usuarios === false || response.estado === 0) {
                        sweetAlert(3, response.exception || 'No hay usuarios registrados.', 'registro.html');
                    }
                });
            }
            sweetAlert(3, 'No se pudo verificar el estado de usuarios.');
        })
        .catch((error) => {
            console.error('Error en la petición:', error);
            sweetAlert(2, 'No se pudo conectar con el servidor.');
        });
});

document.getElementById('login_form').addEventListener('submit', function (event) {
    event.preventDefault();
    const usuario = document.getElementById('usuario').value.trim();
    const contra = document.getElementById('contra').value;
    const boton = this.querySelector('input[type="submit"]');

    if (contra.length < 6) {
        sweetAlert(2, 'La contraseña debe tener al menos 6 caracteres.');
        return;
    }

    if (boton) {
        boton.disabled = true;
        boton.value = 'Ingresando…';
    }

    fetch(API_LOGIN + 'login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario, contra }),
    })
        .then((response) =>
            response.json().then((data) => {
                if (!response.ok) {
                    throw new Error(mensajeDesdeDetail(data.detail, 'Error desconocido'));
                }
                return data;
            }),
        )
        .then((data) => {
            if (data.token_usuario && data.token_tarjeta) {
                localStorage.setItem('token_usuario', data.token_usuario);
                localStorage.setItem('token_tarjeta', data.token_tarjeta);
                if (data.refresh_token) {
                    localStorage.setItem('refresh_token', data.refresh_token);
                }
                sweetAlert(1, data.mensaje, 'dashboard.html');
            } else {
                sweetAlert(2, 'No se recibió un token válido del servidor.');
            }
        })
        .catch((error) => {
            const mensaje = error.message || 'No se pudo iniciar sesión.';
            if (typeof sweetAlert === 'function') {
                sweetAlert(2, mensaje);
            } else if (typeof Swal !== 'undefined' && Swal.fire) {
                Swal.fire({ title: 'Error', text: mensaje, icon: 'error', confirmButtonText: 'Aceptar' });
            } else {
                alert(mensaje);
            }
        })
        .finally(() => {
            if (boton) {
                boton.disabled = false;
                boton.value = 'Iniciar sesión';
            }
        });
});

document.getElementById('togglePassword')?.addEventListener('click', function () {
    const passwordField = document.getElementById('contra');
    const passwordToggle = this.querySelector('img');
    if (!passwordField || !passwordToggle) return;

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        passwordToggle.src = '/resources/icons/ver.png';
    } else {
        passwordField.type = 'password';
        passwordToggle.src = '/resources/icons/ocultar.png';
    }
});

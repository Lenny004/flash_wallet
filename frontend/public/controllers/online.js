// Header de sesión — los pagos recurrentes los procesa el worker del backend.
const API_LOGIN = window.FLASH_API_BASE + '/api/usuarios/';

document.addEventListener('DOMContentLoaded', function () {
    const token_usuario = localStorage.getItem('token_usuario');
    if (!token_usuario) {
        sweetAlert(3, "No hay sesión activa. Redirigiendo al login...", "login.html");
        return;
    }
    apiFetchAuth(API_LOGIN + "readOne", {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    }, 'usuario')
    .then((request) => {
        if (request.ok) {
            return request.json();
        }
        return request.json().then((error) => {
            console.error('Error en la solicitud:', error);
            throw new Error(error.detail || "Error al cargar los datos.");
        });
    })
    .then((response) => {
        if (response.estado) {
            const header = `
                <div class="pill">
                    <p>¡Bienvenido, ${response.usuario}!</p>
                </div>
                <div class="perfil">
                    <a href="perfil.html">
                        <img src="/resources/imgs/default_user.jpg" alt="profile-image">
                    </a>
                </div>`;
            document.getElementById('header').innerHTML = header;
        } else {
            sweetAlert(3, response.exception || 'Ocurrió un error.', "login.html");
        }
    })
    .catch((error) => {
        console.error('Error:', error.message);
        sweetAlert(3, error.message, "login.html");
    });
});

function cerrarSesion() {
    localStorage.removeItem('token_usuario');
    localStorage.removeItem('token_tarjeta');
    localStorage.removeItem('refresh_token');
    sweetAlert(1, "Sesión cerrada exitosamente.", "login.html");
}

const API_REGISTRO = window.FLASH_API_BASE + '/api/usuarios/';

document.getElementById('togglePassword')?.addEventListener('click', function (event) {
    event.preventDefault();
    const passwordField = document.getElementById('contra');
    const passwordToggle = this.querySelector('img');
    if (!passwordField || !passwordToggle) return;

    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        passwordToggle.src = '/resources/icons/ver.png';
        this.setAttribute('aria-pressed', 'true');
        this.setAttribute('aria-label', 'Ocultar contraseña');
    } else {
        passwordField.type = 'password';
        passwordToggle.src = '/resources/icons/ocultar.png';
        this.setAttribute('aria-pressed', 'false');
        this.setAttribute('aria-label', 'Mostrar contraseña');
    }
});

// Método manejador de eventos que se ejecuta cuando se envía el formulario de guardar.
document.getElementById('perfil_form').addEventListener('submit', function (event) {
    event.preventDefault();  // Evitar recarga de página al enviar el formulario

    fetch(API_REGISTRO, {
        method: 'post',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(Object.fromEntries(new FormData(event.target)))
    }).then((request) => {
        if (request.ok) {
            request.json().then((response) => {
                // Guardamos los datos en localStorage
                localStorage.setItem('nuevo_usuario', JSON.stringify(response.nuevo_usuario));
                localStorage.setItem('tarjeta', JSON.stringify(response.tarjeta));
                sweetAlert(1, response.mensaje, "tarjeta_digital.html");
            });
        } else {
            sweetAlert(2, request.statusText);
        }
    }).catch((error) => {
        console.error('Error en la petición:', error);
    });
});

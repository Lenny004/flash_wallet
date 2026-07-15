// Constante para establecer la ruta y parámetros de comunicación con la API en Flask.
const API_LOGIN = 'http://127.0.0.1:8000/api/usuarios/'; // Cambia según la ruta de tu servidor Flask
const URL_PROCESAR_PAGOS = 'http://127.0.0.1:8000/api/transaccion/procesar_pagos';

// Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    const token_usuario = localStorage.getItem('token_usuario');  // Obtener el token almacenado
    if (!token_usuario) {
        // Si no hay token, redirige al login
        sweetAlert(3, "No hay sesión activa. Redirigiendo al login...", "login.html");
        return;
    }
    // Llamada a la API para obtener los datos del usuario
    fetch(API_LOGIN + "readOne", {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token_usuario}`  // Asegúrate de que el token esté siendo enviado correctamente
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
            // Si la respuesta tiene éxito, se muestra el encabezado de bienvenida
            let header = `
                <div class="pill">
                    <p>¡Bienvenido, ${response.usuario}!</p>
                </div>
                <div class="perfil">
                    <a href="perfil.html">
                        <img src="../resources/imgs/default_user.jpg" alt="profile-image">
                    </a>
                </div>`;
            document.getElementById('header').innerHTML = header;
        } else {
            // Si la respuesta contiene un error, mostrar un mensaje
            sweetAlert(3, response.exception || 'Ocurrió un error.', "login.html");
        }
    })
    .catch((error) => {
        // Capturar y mostrar cualquier error ocurrido en la llamada
        console.error('Error:', error.message);
        sweetAlert(3, error.message, "login.html");  // Redirigir al login en caso de error
    });
});


function cerrarSesion() {
    localStorage.removeItem('token');
    sweetAlert(1, "Sesión cerrada exitosamente.", "login.html");
}

// Función para llamar al endpoint de procesamiento de pagos
function procesarPagos() {
    fetch(URL_PROCESAR_PAGOS, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'}
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail || "Error al procesar pagos.");
            });
        }
        return response.json();
    })
    .then(data => {
        console.log("Pagos procesados exitosamente:", data);
    })
    .catch(error => {
        console.error("Error al procesar pagos:", error.message);
        sweetAlert(2, error.message); // Muestra una alerta en caso de error
    });
}

// Llamar a la función procesarPagos cada 5 segundos
setInterval(procesarPagos, 5000);

const token_usuario = localStorage.getItem('token_usuario');  // Obtener el token almacenado
var contador = 1;

// Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    cargarDatos();
});

function cargarDatos() {
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
            document.getElementById('nombres').value = response.nombres;
            document.getElementById('apellidos').value = response.apellidos;
            document.getElementById('email').value = response.email;
            document.getElementById('direccion').value = response.direccion;
            document.getElementById('telefono').value = response.telefono;
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

function habilitarEdit(){
    const inputs = document.querySelectorAll(".miInput");
    // Seleccionar el primer botón con la clase "subrayar"
    let btnedit = document.querySelector('.subrayar');
    if (contador == 1) {
        // Si la respuesta contiene un error, mostrar un mensaje
        sweetAlert(1, 'Se ha habilitado la edición de datos', null);
        // Cambiar el texto del botón
        if (btnedit) {
            btnedit.innerText = "Deshabilitar Editar ✏️";
        }
        inputs.forEach(input => {
            input.disabled = false;
            input.style.color = "#9E2D2D"
            input.style.fontWeight = "bold";
        });
        contador = 2;
    } else {
        // Si la respuesta contiene un error, mostrar un mensaje
        sweetAlert(3, 'Se ha deshabilitado la edición de datos', null);
        // Cambiar el texto del botón
        if (btnedit) {
            btnedit.innerText = "Habilitar Editar ✏️";
        }
        inputs.forEach(input => {
            input.disabled = true;
            input.style.color = "#545454"
            input.style.fontWeight = "normal";
        });
        contador = 1
    }
}

document.getElementById("perfil_form").addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevenir el recargado de la página

    // Encontrar el botón de envío
    const botonEnviar = document.getElementById('btnUpdate');
    // Mostrar un indicador de carga mientras se realiza la solicitud
    botonEnviar.disabled = true; // Desactiva el botón para evitar múltiples envíos
    botonEnviar.textContent = "Actualizando...";

    try {
        // Convertir el formulario a un objeto JSON
        const formData = Object.fromEntries(new FormData(event.target));
        
        // Validar campos (opcional, basado en las necesidades del formulario)
        if (!formData.email || !formData.telefono) {
            throw new Error("Por favor, completa los campos obligatorios.");
        }

        // Hacer la petición al servidor
        const response = await fetch(API_LOGIN + 'update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token_usuario}`
            },
            body: JSON.stringify(formData),
        });

        // Procesar la respuesta del servidor
        const data = await response.json();
        if (!response.ok) {
            // Si el servidor devuelve un error, mostramos el mensaje
            throw new Error(data.detail || "Ocurrió un error al actualizar el perfil.");
        }
        cargarDatos();
        habilitarEdit();
        // Mostrar un mensaje de éxito
        sweetAlert(1, "Perfil actualizado exitosamente.");
        // Aquí podrías actualizar la UI con los nuevos datos del usuario si es necesario.
    } catch (error) {
        // Mostrar el error al usuario
        sweetAlert(2, error.message);
    } finally {
        // Restaurar el estado inicial del botón
        botonEnviar.disabled = false;
        botonEnviar.textContent = "Actualizar perfil";
    }
});

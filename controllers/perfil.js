var contador = 1;

// Evento que se ejecuta cuando se carga la página web
document.addEventListener('DOMContentLoaded', function () {
    cargarDatos();
});

function cargarDatos() {
    if (!localStorage.getItem('token_usuario')) {
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
        } else {
            return request.json().then((error) => {
                console.error('Error en la solicitud:', error);
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
            sweetAlert(3, response.exception || 'Ocurrió un error.', null);
        }
    })
    .catch((error) => {
        console.error('Error:', error.message);
        sweetAlert(3, error.message, "login.html");
    });
}

function habilitarEdit(){
    const inputs = document.querySelectorAll(".miInput");
    let btnedit = document.querySelector('.subrayar');
    if (contador == 1) {
        sweetAlert(1, 'Se ha habilitado la edición de datos', null);
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
        sweetAlert(3, 'Se ha deshabilitado la edición de datos', null);
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
    event.preventDefault();

    const botonEnviar = document.getElementById('btnUpdate');
    botonEnviar.disabled = true;
    botonEnviar.textContent = "Actualizando...";

    try {
        const formData = Object.fromEntries(new FormData(event.target));

        if (!formData.email || !formData.telefono) {
            throw new Error("Por favor, completa los campos obligatorios.");
        }

        const response = await apiFetchAuth(API_LOGIN + 'update', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
        }, 'usuario');

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Ocurrió un error al actualizar el perfil.");
        }
        cargarDatos();
        habilitarEdit();
        sweetAlert(1, "Perfil actualizado exitosamente.");
    } catch (error) {
        sweetAlert(2, error.message);
    } finally {
        botonEnviar.disabled = false;
        botonEnviar.textContent = "Actualizar perfil";
    }
});

function tarjeta() {
    // Recuperar los datos almacenados en localStorage
    const datos_usuario = JSON.parse(localStorage.getItem('nuevo_usuario'));
    const datos_tarjeta = JSON.parse(localStorage.getItem('tarjeta'));

    if (datos_usuario && datos_tarjeta) {
        let content = [];
        content.push(`
            <p><b>${datos_tarjeta.pan}</b></p>
            <p><b>DESDE: ${datos_tarjeta.fecha_creacion}</b></p>
            <p><b>CVC: ${datos_tarjeta.cvc}</b></p>
            <p><b>${datos_usuario.nombres} ${datos_usuario.apellidos}</b></p>`);

        // Se agregan las filas al cuerpo de la tabla
        document.getElementById('datos_tarjeta').innerHTML = content.join('');
    } else {
        console.error('No se encontraron los datos en localStorage');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Llamar a la función tarjeta para mostrar los datos
    tarjeta();
});

function loginContinue() {
    window.location.href = 'login.html';  // Redirigir a tarjeta_digital.html
}
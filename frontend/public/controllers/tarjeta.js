function formatearPan(pan) {
    const digitos = String(pan).replace(/\D/g, '');
    return digitos.replace(/(\d{4})(?=\d)/g, '$1 ').trim() || pan;
}

function plantillaTarjetaDigital({ pan, fecha, cvc, titular }) {
    return `
      <img
        class="tarjeta_digital__img"
        src="/resources/imgs/Tarjeta.png"
        alt=""
        aria-hidden="true"
        draggable="false"
      />
      <div class="tarjeta_digital__face">
        <p class="tarjeta_digital__pan">${formatearPan(pan)}</p>
        <div class="tarjeta_digital__row tarjeta_digital__row--meta">
          <div class="tarjeta_digital__field">
            <span class="tarjeta_digital__label">Desde</span>
            <span class="tarjeta_digital__value">${fecha}</span>
          </div>
          <div class="tarjeta_digital__field">
            <span class="tarjeta_digital__label">CVC</span>
            <span class="tarjeta_digital__value">${cvc}</span>
          </div>
        </div>
        <p class="tarjeta_digital__holder">${titular}</p>
      </div>`;
}

function tarjeta() {
    const datos_usuario = JSON.parse(localStorage.getItem('nuevo_usuario'));
    const datos_tarjeta = JSON.parse(localStorage.getItem('tarjeta'));

    if (datos_usuario && datos_tarjeta) {
        document.getElementById('datos_tarjeta').innerHTML = plantillaTarjetaDigital({
            pan: datos_tarjeta.pan,
            fecha: datos_tarjeta.fecha_creacion,
            cvc: datos_tarjeta.cvc,
            titular: `${datos_usuario.nombres} ${datos_usuario.apellidos}`,
        });
    } else {
        console.error('No se encontraron los datos en localStorage');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    tarjeta();
});

function loginContinue() {
    window.location.href = 'login.html';
}

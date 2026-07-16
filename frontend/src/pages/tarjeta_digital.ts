/**
 * @file Página de tarjeta digital: muestra datos recién registrados y redirige al login.
 */

interface DatosUsuario {
  nombres: string;
  apellidos: string;
}

interface DatosTarjeta {
  pan: string;
  fecha_creacion: string;
  cvc: string;
}

/** Formatea el PAN en grupos de 4 dígitos. */
function formatearPan(pan: string): string {
  const digitos = String(pan).replace(/\D/g, '');
  return digitos.replace(/(\d{4})(?=\d)/g, '$1 ').trim() || pan;
}

/** Plantilla HTML de la cara de la tarjeta digital. */
function plantillaTarjetaDigital(opciones: {
  pan: string;
  fecha: string;
  cvc: string;
  titular: string;
}): string {
  return `
    <img
      class="tarjeta_digital__img"
      src="/resources/imgs/Tarjeta.png"
      alt=""
      aria-hidden="true"
      draggable="false"
    />
    <div class="tarjeta_digital__face">
      <p class="tarjeta_digital__pan">${formatearPan(opciones.pan)}</p>
      <div class="tarjeta_digital__row tarjeta_digital__row--meta">
        <div class="tarjeta_digital__field">
          <span class="tarjeta_digital__label">Desde</span>
          <span class="tarjeta_digital__value">${opciones.fecha}</span>
        </div>
        <div class="tarjeta_digital__field">
          <span class="tarjeta_digital__label">CVC</span>
          <span class="tarjeta_digital__value">${opciones.cvc}</span>
        </div>
      </div>
      <p class="tarjeta_digital__holder">${opciones.titular}</p>
    </div>`;
}

/**
 * Muestra los datos de la tarjeta digital recién creada desde localStorage.
 * Lee `nuevo_usuario` y `tarjeta` guardados tras el registro.
 */
function mostrarTarjetaDigital(): void {
  const datosUsuario = JSON.parse(
    localStorage.getItem('nuevo_usuario') || 'null',
  ) as DatosUsuario | null;
  const datosTarjeta = JSON.parse(
    localStorage.getItem('tarjeta') || 'null',
  ) as DatosTarjeta | null;

  if (datosUsuario && datosTarjeta) {
    const contenedorTarjeta = document.getElementById('datos_tarjeta');
    if (contenedorTarjeta) {
      contenedorTarjeta.innerHTML = plantillaTarjetaDigital({
        pan: datosTarjeta.pan,
        fecha: datosTarjeta.fecha_creacion,
        cvc: datosTarjeta.cvc,
        titular: `${datosUsuario.nombres} ${datosUsuario.apellidos}`,
      });
    }
  } else {
    console.error('No se encontraron los datos en localStorage');
  }
}

/** Redirige al usuario a la página de inicio de sesión. */
function continuarAlLogin(): void {
  window.location.href = 'login.html';
}

declare global {
  interface Window {
    loginContinue: () => void;
  }
}

window.loginContinue = continuarAlLogin;

document.addEventListener('DOMContentLoaded', () => {
  mostrarTarjetaDigital();
});

export {};

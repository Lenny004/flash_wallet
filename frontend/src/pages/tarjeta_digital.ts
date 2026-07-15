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
    const htmlTarjeta = `
            <p><b>${datosTarjeta.pan}</b></p>
            <p><b>DESDE: ${datosTarjeta.fecha_creacion}</b></p>
            <p><b>CVC: ${datosTarjeta.cvc}</b></p>
            <p><b>${datosUsuario.nombres} ${datosUsuario.apellidos}</b></p>`;
    const contenedorTarjeta = document.getElementById('datos_tarjeta');
    if (contenedorTarjeta) contenedorTarjeta.innerHTML = htmlTarjeta;
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

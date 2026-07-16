/**
 * @file Página de inicio de sesión: verificación de estado, login y toggle de contraseña.
 */

import { getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<unknown>;
};

const urlApiLogin = `${getApiBase()}/api/usuarios/`;

/** Códigos de tipo de alerta SweetAlert usados en la página. */
type TipoAlerta = 1 | 2 | 3 | 4 | 5;

/**
 * Muestra una alerta SweetAlert según el tipo indicado.
 * @param tipoAlerta - 1 éxito, 2 error, 3 advertencia, 4 aviso, 5 campos vacíos.
 * @param texto - Mensaje a mostrar al usuario.
 * @param urlRedireccion - URL opcional; si se indica, redirige al confirmar.
 */
function mostrarAlerta(tipoAlerta: TipoAlerta, texto: string, urlRedireccion?: string): void {
  let titulo: string;
  let icono: string;
  switch (tipoAlerta) {
    case 1:
      titulo = 'Éxito';
      icono = 'success';
      break;
    case 2:
      titulo = 'Error';
      icono = 'error';
      break;
    case 3:
      titulo = 'Advertencia';
      icono = 'warning';
      break;
    case 4:
      titulo = 'Aviso';
      icono = 'info';
      break;
    case 5:
      titulo = 'Campos Vacios';
      icono = 'warning';
      break;
  }

  if (urlRedireccion) {
    Swal.fire({
      title: titulo,
      text: texto,
      icon: icono,
      confirmButtonText: 'Aceptar',
      allowOutsideClick: false,
      allowEscapeKey: false,
      allowEnterKey: true,
      stopKeydownPropagation: false,
    }).then(() => {
      location.href = urlRedireccion;
    });
  } else {
    Swal.fire({
      toast: true,
      position: 'bottom-end',
      timer: 5000,
      timerProgressBar: true,
      title: titulo,
      text: texto,
      icon: icono,
      color: '#9e2d2d',
      background: '#fffff',
      customClass: {
        popup: 'custom-swal-popup',
      },
      showConfirmButton: false,
      stopKeydownPropagation: false,
    });
  }
}

/** Respuesta del GET inicial que verifica sesión y existencia de usuarios. */
interface RespuestaVerificacionUsuarios {
  session?: boolean;
  hay_usuarios?: boolean;
  estado?: number;
  exception?: string;
}

/** Respuesta del endpoint de login con tokens y mensajes. */
interface RespuestaLogin {
  token_usuario?: string;
  token_tarjeta?: string;
  refresh_token?: string;
  mensaje?: string;
  detail?: string;
}

document.addEventListener('DOMContentLoaded', () => {
  fetch(urlApiLogin, { method: 'GET' })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        respuestaApi.json().then((datos: RespuestaVerificacionUsuarios) => {
          if (datos.session) {
            location.href = 'dashboard.html';
          } else if (datos.hay_usuarios === false || datos.estado === 0) {
            mostrarAlerta(3, datos.exception || 'No hay usuarios registrados.', 'registro.html');
          } else {
            Swal.fire({
              title: 'Bienvenido a Flash',
              text: 'Ya puede ingresar al sistema',
              imageUrl: '/resources/imgs/Flash_logo.png',
              imageWidth: 80,
              imageHeight: 80,
              imageAlt: 'Custom image',
              confirmButtonText: 'Continuar',
              allowOutsideClick: false,
              allowEscapeKey: false,
              allowEnterKey: true,
              stopKeydownPropagation: false,
            });
          }
        });
      } else {
        mostrarAlerta(3, 'No se pudo verificar el estado de usuarios.');
      }
    })
    .catch((error: unknown) => {
      console.error('Error en la petición:', error);
    });
});

const formularioLogin = document.getElementById('login_form');
formularioLogin?.addEventListener('submit', (evento) => {
  evento.preventDefault();

  const usuario = (document.getElementById('usuario') as HTMLInputElement).value;
  const contra = (document.getElementById('contra') as HTMLInputElement).value;

  fetch(`${urlApiLogin}login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, contra }),
  })
    .then((respuestaApi) =>
      respuestaApi.json().then((datos: RespuestaLogin) => {
        if (!respuestaApi.ok) {
          throw new Error(datos.detail || 'Error desconocido');
        }
        return datos;
      }),
    )
    .then((datosLogin) => {
      if (datosLogin.token_usuario && datosLogin.token_tarjeta) {
        localStorage.setItem('token_usuario', datosLogin.token_usuario);
        localStorage.setItem('token_tarjeta', datosLogin.token_tarjeta);
        if (datosLogin.refresh_token) {
          localStorage.setItem('refresh_token', datosLogin.refresh_token);
        }
        mostrarAlerta(1, datosLogin.mensaje || 'Inicio de sesión exitoso', 'dashboard.html');
      } else {
        mostrarAlerta(2, 'No se recibió un token válido del servidor.');
      }
    })
    .catch((error: Error) => {
      mostrarAlerta(2, error.message);
    });
});

const botonTogglePassword = document.getElementById('togglePassword');
botonTogglePassword && (botonTogglePassword.onclick = function (evento) {
  evento.preventDefault();
  evento.stopPropagation();

  const campoPassword = document.getElementById('contra') as HTMLInputElement | null;
  if (!campoPassword || !botonTogglePassword) return;

  const mostrar = campoPassword.type === 'password';
  campoPassword.type = mostrar ? 'text' : 'password';

  const iconoToggle = botonTogglePassword.querySelector('img');
  if (iconoToggle) {
    iconoToggle.setAttribute(
      'src',
      mostrar ? '/resources/icons/ver.png' : '/resources/icons/ocultar.png',
    );
  }
});

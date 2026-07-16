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
 * Normaliza el `detail` de FastAPI (string, lista de errores de validación u objeto).
 */
function mensajeDesdeDetail(detail: unknown, fallback = 'Error desconocido'): string {
  if (typeof detail === 'string' && detail.trim() !== '') {
    return detail;
  }
  if (Array.isArray(detail)) {
    const partes = detail.map((item) => {
      if (typeof item === 'string') return item;
      if (item && typeof item === 'object' && 'msg' in item) {
        return String((item as { msg: unknown }).msg);
      }
      return '';
    }).filter(Boolean);
    if (partes.length > 0) return partes.join(' ');
  }
  return fallback;
}

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

  void Swal.fire({
    title: titulo,
    text: texto,
    icon: icono,
    confirmButtonText: 'Aceptar',
    allowOutsideClick: Boolean(urlRedireccion),
    allowEscapeKey: true,
    allowEnterKey: true,
  }).then(() => {
    if (urlRedireccion) {
      location.href = urlRedireccion;
    }
  });
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
  detail?: unknown;
}

document.addEventListener('DOMContentLoaded', () => {
  fetch(urlApiLogin, { method: 'GET' })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json().then((datos: RespuestaVerificacionUsuarios) => {
          if (datos.session) {
            location.href = 'dashboard.html';
          } else if (datos.hay_usuarios === false || datos.estado === 0) {
            mostrarAlerta(3, datos.exception || 'No hay usuarios registrados.', 'registro.html');
          }
        });
      }
      mostrarAlerta(3, 'No se pudo verificar el estado de usuarios.');
    })
    .catch((error: unknown) => {
      console.error('Error en la petición:', error);
      mostrarAlerta(2, 'No se pudo conectar con el servidor. ¿Está la API en marcha?');
    });
});

const formularioLogin = document.getElementById('login_form');
const botonSubmit = formularioLogin?.querySelector<HTMLInputElement>('input[type="submit"]');

formularioLogin?.addEventListener('submit', (evento) => {
  evento.preventDefault();

  const usuario = (document.getElementById('usuario') as HTMLInputElement).value.trim();
  const contra = (document.getElementById('contra') as HTMLInputElement).value;

  if (!usuario || !contra) {
    mostrarAlerta(5, 'Completa usuario y contraseña.');
    return;
  }

  if (contra.length < 6) {
    mostrarAlerta(2, 'La contraseña debe tener al menos 6 caracteres.');
    return;
  }

  if (botonSubmit) {
    botonSubmit.disabled = true;
    botonSubmit.value = 'Ingresando…';
  }

  fetch(`${urlApiLogin}login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, contra }),
  })
    .then(async (respuestaApi) => {
      let datos: RespuestaLogin = {};
      try {
        datos = (await respuestaApi.json()) as RespuestaLogin;
      } catch {
        throw new Error('Respuesta inválida del servidor.');
      }
      if (!respuestaApi.ok) {
        throw new Error(mensajeDesdeDetail(datos.detail, `Error ${respuestaApi.status}`));
      }
      return datos;
    })
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
    .catch((error: unknown) => {
      const mensaje =
        error instanceof Error && error.message
          ? error.message
          : 'No se pudo iniciar sesión.';
      mostrarAlerta(2, mensaje);
    })
    .finally(() => {
      if (botonSubmit) {
        botonSubmit.disabled = false;
        botonSubmit.value = 'Iniciar sesión';
      }
    });
});

const botonTogglePassword = document.getElementById('togglePassword');
botonTogglePassword &&
  (botonTogglePassword.onclick = function (evento) {
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

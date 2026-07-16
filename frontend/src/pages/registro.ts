/**
 * @file Página de registro de usuario: envío del formulario y almacenamiento de tokens.
 */

import { getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<unknown>;
};

const urlApiRegistro = `${getApiBase()}/api/usuarios/`;

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

/** Respuesta del endpoint de registro con usuario, tarjeta y tokens. */
interface RespuestaRegistro {
  mensaje?: string;
  nuevo_usuario?: Record<string, unknown>;
  tarjeta?: Record<string, unknown>;
  token_usuario?: string;
  token_tarjeta?: string;
  refresh_token?: string;
  detail?: string;
}

const formularioRegistro = document.getElementById('perfil_form');
formularioRegistro?.addEventListener('submit', (evento) => {
  evento.preventDefault();

  const formulario = evento.target as HTMLFormElement;
  const datosFormulario = Object.fromEntries(new FormData(formulario));

  fetch(urlApiRegistro, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datosFormulario),
  })
    .then((respuestaApi) =>
      respuestaApi.json().then((datos: RespuestaRegistro) => {
        if (!respuestaApi.ok) {
          throw new Error(datos.detail || respuestaApi.statusText || 'Error desconocido');
        }
        return datos;
      }),
    )
    .then((datosRegistro) => {
      if (datosRegistro.nuevo_usuario) {
        localStorage.setItem('nuevo_usuario', JSON.stringify(datosRegistro.nuevo_usuario));
      }
      if (datosRegistro.tarjeta) {
        localStorage.setItem('tarjeta', JSON.stringify(datosRegistro.tarjeta));
      }
      if (datosRegistro.token_usuario) {
        localStorage.setItem('token_usuario', datosRegistro.token_usuario);
      }
      if (datosRegistro.token_tarjeta) {
        localStorage.setItem('token_tarjeta', datosRegistro.token_tarjeta);
      }
      if (datosRegistro.refresh_token) {
        localStorage.setItem('refresh_token', datosRegistro.refresh_token);
      }

      mostrarAlerta(1, datosRegistro.mensaje || 'Registro exitoso', 'tarjeta_digital.html');
    })
    .catch((error: Error) => {
      mostrarAlerta(2, error.message);
    });
});

function alternarVisibilidadContrasena(): void {
  const campoPassword = document.getElementById('contra') as HTMLInputElement | null;
  const botonTogglePassword = document.getElementById('togglePassword');
  const iconoToggle = botonTogglePassword?.querySelector('img');
  if (!campoPassword || !botonTogglePassword || !iconoToggle) return;

  const mostrar = campoPassword.type === 'password';
  campoPassword.setAttribute('type', mostrar ? 'text' : 'password');
  iconoToggle.setAttribute(
    'src',
    mostrar ? '/resources/icons/ver.png' : '/resources/icons/ocultar.png',
  );
  botonTogglePassword.setAttribute('aria-pressed', mostrar ? 'true' : 'false');
  botonTogglePassword.setAttribute(
    'aria-label',
    mostrar ? 'Ocultar contraseña' : 'Mostrar contraseña',
  );
}

const botonTogglePassword = document.getElementById('togglePassword');
// onclick (no addEventListener) evita listeners duplicados con HMR de Vite
if (botonTogglePassword) {
  botonTogglePassword.onclick = (evento) => {
    evento.preventDefault();
    evento.stopPropagation();
    alternarVisibilidadContrasena();
  };
}

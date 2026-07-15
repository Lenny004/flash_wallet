import { getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<unknown>;
};

const API_LOGIN = `${getApiBase()}/api/usuarios/`;

type AlertType = 1 | 2 | 3 | 4 | 5;

function sweetAlert(type: AlertType, text: string, url?: string): void {
  let title: string;
  let icon: string;
  switch (type) {
    case 1:
      title = 'Éxito';
      icon = 'success';
      break;
    case 2:
      title = 'Error';
      icon = 'error';
      break;
    case 3:
      title = 'Advertencia';
      icon = 'warning';
      break;
    case 4:
      title = 'Aviso';
      icon = 'info';
      break;
    case 5:
      title = 'Campos Vacios';
      icon = 'warning';
      break;
  }

  if (url) {
    Swal.fire({
      title,
      text,
      icon,
      confirmButtonText: 'Aceptar',
      allowOutsideClick: false,
      allowEscapeKey: false,
      allowEnterKey: true,
      stopKeydownPropagation: false,
    }).then(() => {
      location.href = url;
    });
  } else {
    Swal.fire({
      toast: true,
      position: 'bottom-end',
      timer: 5000,
      timerProgressBar: true,
      title,
      text,
      icon,
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

interface UsuariosCheckResponse {
  session?: boolean;
  hay_usuarios?: boolean;
  estado?: number;
  exception?: string;
}

interface LoginResponse {
  token_usuario?: string;
  token_tarjeta?: string;
  refresh_token?: string;
  mensaje?: string;
  detail?: string;
}

document.addEventListener('DOMContentLoaded', () => {
  fetch(API_LOGIN, { method: 'GET' })
    .then((request) => {
      if (request.ok) {
        request.json().then((response: UsuariosCheckResponse) => {
          if (response.session) {
            location.href = 'dashboard.html';
          } else if (response.hay_usuarios === false || response.estado === 0) {
            sweetAlert(3, response.exception || 'No hay usuarios registrados.', 'registro.html');
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
        sweetAlert(3, 'No se pudo verificar el estado de usuarios.');
      }
    })
    .catch((error: unknown) => {
      console.error('Error en la petición:', error);
    });
});

const loginForm = document.getElementById('login_form');
loginForm?.addEventListener('submit', (event) => {
  event.preventDefault();

  const usuario = (document.getElementById('usuario') as HTMLInputElement).value;
  const contra = (document.getElementById('contra') as HTMLInputElement).value;

  fetch(`${API_LOGIN}login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, contra }),
  })
    .then((response) =>
      response.json().then((data: LoginResponse) => {
        if (!response.ok) {
          throw new Error(data.detail || 'Error desconocido');
        }
        return data;
      }),
    )
    .then((data) => {
      if (data.token_usuario && data.token_tarjeta) {
        localStorage.setItem('token_usuario', data.token_usuario);
        localStorage.setItem('token_tarjeta', data.token_tarjeta);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        sweetAlert(1, data.mensaje || 'Inicio de sesión exitoso', 'dashboard.html');
      } else {
        sweetAlert(2, 'No se recibió un token válido del servidor.');
      }
    })
    .catch((error: Error) => {
      sweetAlert(2, error.message);
    });
});

const togglePassword = document.getElementById('togglePassword');
togglePassword?.addEventListener('click', function (this: HTMLElement) {
  const passwordField = document.getElementById('contra') as HTMLInputElement;
  const passwordToggle = this.querySelector('img');

  if (passwordField.type === 'password') {
    passwordField.type = 'text';
    if (passwordToggle) passwordToggle.setAttribute('src', '/resources/icons/ver.png');
  } else {
    passwordField.type = 'password';
    if (passwordToggle) passwordToggle.setAttribute('src', '/resources/icons/ocultar.png');
  }
});

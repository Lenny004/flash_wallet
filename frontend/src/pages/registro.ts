import { getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<unknown>;
};

const API_REGISTRO = `${getApiBase()}/api/usuarios/`;

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

interface RegistroResponse {
  mensaje?: string;
  nuevo_usuario?: Record<string, unknown>;
  tarjeta?: Record<string, unknown>;
  token_usuario?: string;
  token_tarjeta?: string;
  refresh_token?: string;
  detail?: string;
}

const perfilForm = document.getElementById('perfil_form');
perfilForm?.addEventListener('submit', (event) => {
  event.preventDefault();

  const form = event.target as HTMLFormElement;
  const body = Object.fromEntries(new FormData(form));

  fetch(API_REGISTRO, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
    .then((response) =>
      response.json().then((data: RegistroResponse) => {
        if (!response.ok) {
          throw new Error(data.detail || response.statusText || 'Error desconocido');
        }
        return data;
      }),
    )
    .then((response) => {
      if (response.nuevo_usuario) {
        localStorage.setItem('nuevo_usuario', JSON.stringify(response.nuevo_usuario));
      }
      if (response.tarjeta) {
        localStorage.setItem('tarjeta', JSON.stringify(response.tarjeta));
      }
      if (response.token_usuario) {
        localStorage.setItem('token_usuario', response.token_usuario);
      }
      if (response.token_tarjeta) {
        localStorage.setItem('token_tarjeta', response.token_tarjeta);
      }
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }

      sweetAlert(1, response.mensaje || 'Registro exitoso', 'tarjeta_digital.html');
    })
    .catch((error: Error) => {
      sweetAlert(2, error.message);
    });
});

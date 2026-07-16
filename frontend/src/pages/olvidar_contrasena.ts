/**
 * @file Recuperación de contraseña: solicitar código y restablecer.
 */

import { getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<unknown>;
};

const urlApi = `${getApiBase()}/api/usuarios/`;

type TipoAlerta = 1 | 2 | 3 | 4 | 5;

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

interface RespuestaForgot {
  estado?: number;
  mensaje?: string;
  codigo?: string;
  detail?: string;
}

interface RespuestaReset {
  estado?: number;
  mensaje?: string;
  detail?: string;
}

let pasoCodigoActivo = false;

function activarPasoCodigo(codigoOpcional?: string): void {
  pasoCodigoActivo = true;
  const bloque = document.getElementById('paso-codigo');
  const descripcion = document.getElementById('paso-descripcion');
  const boton = document.getElementById('btn_recuperar') as HTMLInputElement | null;
  const campoCodigo = document.getElementById('codigo') as HTMLInputElement | null;
  const campoNueva = document.getElementById('nueva_contra') as HTMLInputElement | null;
  const campoConfirmar = document.getElementById('confirmar_contra') as HTMLInputElement | null;

  bloque?.classList.remove('paso-oculto');
  if (descripcion) {
    descripcion.textContent = 'Ingresa el código y tu nueva contraseña';
  }
  if (boton) boton.value = 'Restablecer contraseña';
  if (campoCodigo) {
    campoCodigo.required = true;
    if (codigoOpcional) campoCodigo.value = codigoOpcional;
  }
  if (campoNueva) campoNueva.required = true;
  if (campoConfirmar) campoConfirmar.required = true;
}

const formulario = document.getElementById('forgot_form');
formulario?.addEventListener('submit', (evento) => {
  evento.preventDefault();

  const email = (document.getElementById('email') as HTMLInputElement).value.trim();

  if (!pasoCodigoActivo) {
    fetch(`${urlApi}forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    })
      .then((respuestaApi) =>
        respuestaApi.json().then((datos: RespuestaForgot) => {
          if (!respuestaApi.ok) {
            throw new Error(datos.detail || 'No se pudo solicitar el código.');
          }
          return datos;
        }),
      )
      .then((datos) => {
        if (datos.codigo) {
          activarPasoCodigo(datos.codigo);
          mostrarAlerta(
            4,
            `${datos.mensaje || 'Código generado.'} Tu código es: ${datos.codigo}`,
          );
        } else {
          mostrarAlerta(1, datos.mensaje || 'Si el correo existe, recibirás instrucciones.');
        }
      })
      .catch((error: Error) => {
        mostrarAlerta(2, error.message);
      });
    return;
  }

  const codigo = (document.getElementById('codigo') as HTMLInputElement).value.trim();
  const nuevaContra = (document.getElementById('nueva_contra') as HTMLInputElement).value;
  const confirmarContra = (document.getElementById('confirmar_contra') as HTMLInputElement).value;

  if (nuevaContra.length < 6) {
    mostrarAlerta(5, 'La contraseña debe tener al menos 6 caracteres.');
    return;
  }
  if (nuevaContra !== confirmarContra) {
    mostrarAlerta(2, 'Las contraseñas no coinciden.');
    return;
  }

  fetch(`${urlApi}reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      codigo,
      nueva_contra: nuevaContra,
    }),
  })
    .then((respuestaApi) =>
      respuestaApi.json().then((datos: RespuestaReset) => {
        if (!respuestaApi.ok) {
          throw new Error(datos.detail || 'No se pudo restablecer la contraseña.');
        }
        return datos;
      }),
    )
    .then((datos) => {
      mostrarAlerta(1, datos.mensaje || 'Contraseña actualizada.', 'login.html');
    })
    .catch((error: Error) => {
      mostrarAlerta(2, error.message);
    });
});

/**
 * @file Página de recarga de saldo: consulta monto mínimo y procesa recargas.
 */

import { apiFetchAuth, getApiBase, requireCardSession } from '../lib/auth';

/** Guard de sesión: requiere token de tarjeta. */
const sesionOk = requireCardSession();

declare function sweetAlert(type: 1 | 2 | 3 | 4 | 5, text: string, url?: string | null): void;

const urlApiHistorial = `${getApiBase()}/api/historial/`;
const urlApiTransaccion = `${getApiBase()}/api/transaccion/`;

/** Respuesta del endpoint de saldo pendiente mínimo a recargar. */
interface RespuestaSaldoPendiente {
  estado?: boolean;
  monto_pendiente?: number;
  mensaje?: string;
  detail?: string;
}

/** Respuesta del endpoint de recarga de saldo. */
interface RespuestaRecarga {
  estado?: boolean;
  mensaje?: string;
  exception?: string;
  detail?: string;
}

/**
 * Obtiene y muestra el monto mínimo de recarga pendiente en el campo `#minima`.
 * Requiere `token_tarjeta` en localStorage.
 */
function obtenerMontoMinimo(): void {
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }

  apiFetchAuth(`${urlApiTransaccion}saldo_pendiente`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        throw new Error(errorDatos.detail || 'Error desconocido al obtener saldo pendiente');
      });
    })
    .then((datos: RespuestaSaldoPendiente) => {
      if (datos.estado && datos.monto_pendiente !== undefined) {
        const campoMinima = document.getElementById('minima') as HTMLInputElement;
        if (campoMinima) {
          campoMinima.value = `Cantidad minima a recargar: $${datos.monto_pendiente.toFixed(2)}`;
        }
      } else {
        sweetAlert(4, datos.mensaje || 'No se pudo obtener el saldo pendiente', null);
      }
    })
    .catch((error: Error) => {
      sweetAlert(4, error.message, null);
    });
}

document.addEventListener('DOMContentLoaded', () => {
  if (!sesionOk) return;
  obtenerMontoMinimo();
});

const formularioRecarga = document.getElementById('recarga_form');
formularioRecarga?.addEventListener('submit', (evento) => {
  if (!sesionOk) return;
  evento.preventDefault();
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  apiFetchAuth(`${urlApiHistorial}recargar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(new FormData(evento.target as HTMLFormElement))),
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        throw new Error(errorDatos.detail || 'Error desconocido');
      });
    })
    .then((datos: RespuestaRecarga) => {
      if (datos.estado) {
        sweetAlert(1, datos.mensaje || 'Recarga exitosa', null);
      } else {
        sweetAlert(4, datos.exception || 'No hay resultados', null);
      }
    })
    .catch((error: Error) => {
      if (error.message.includes('401')) {
        sweetAlert(3, 'Sesión expirada. Inicia sesión nuevamente.', null);
      } else if (error.message.includes('404')) {
        sweetAlert(3, 'Tarjeta no encontrada.', null);
      } else {
        sweetAlert(4, error.message, null);
      }
    });
});

const botonCancelar = document.querySelector('.cancel');
botonCancelar?.addEventListener('click', () => {
  alert('Operación cancelada.');
});

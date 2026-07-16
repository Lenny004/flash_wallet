/**
 * @file Página de pagos pendientes: listado de transacciones/servicios por pagar.
 */

import { apiFetchAuth, getApiBase, requireCardSession, requireUserSession } from '../lib/auth';

/** Guard de sesión: requiere tokens de usuario y tarjeta. */
const sesionOk = requireUserSession() && requireCardSession();

declare function sweetAlert(type: 1 | 2 | 3 | 4 | 5, text: string, url?: string | null): void;

const urlApiTransaccion = `${getApiBase()}/api/transaccion/`;

/** Fila de transacción devuelta por la API. */
interface FilaTransaccion {
  id_estado: number;
  nombre: string;
  descripcion: string;
  fecha_transaccion: string;
  hora_transaccion: string;
  monto: number | string;
  estado: string;
}

/** Respuesta del endpoint de lectura de transacciones. */
interface RespuestaTransaccion {
  estado?: number;
  dataset?: FilaTransaccion[];
  exception?: string;
}

/**
 * Carga las transacciones pendientes desde la API y las renderiza como tarjetas.
 * @param urlApi - URL completa del endpoint de lectura.
 */
function cargarTransacciones(urlApi: string): void {
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta.', null);
    return;
  }
  apiFetchAuth(urlApi, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        respuestaApi.json().then((datos: RespuestaTransaccion) => {
          if (datos.estado === 1) {
            renderizarTarjetas(datos.dataset ?? []);
          } else {
            sweetAlert(4, `Error en la respuesta: ${datos.exception}`, null);
          }
        });
      } else {
        sweetAlert(2, respuestaApi.statusText, null);
      }
    })
    .catch(() => {
      sweetAlert(4, 'Hubo un problema con la solicitud.', null);
    });
}

/**
 * Renderiza las tarjetas de servicios en el contenedor `#tarjetas_pago`.
 * @param registros - Lista de transacciones devueltas por la API.
 */
function renderizarTarjetas(registros: FilaTransaccion[]): void {
  const tarjetasHtml: string[] = [];
  registros.forEach((fila) => {
    if (fila.id_estado == 1) {
      tarjetasHtml.push(
        `<div class="tarjeta_servicio">
                <div class="datos_servicio">
                    <hr class="estado_p">
                    <h2>${fila.nombre}</h2>
                    <p>${fila.descripcion}</p>
                    <p>Fecha: ${fila.fecha_transaccion} ${fila.hora_transaccion} PM</p>
                    <p>Monto: ${fila.monto}</p>
                </div>
                <div class="estado_servicio">
                    <p class="estado_p"><b>${fila.estado}</b></p>
                </div>
            </div>`,
      );
    } else {
      tarjetasHtml.push(
        `<div class="tarjeta_servicio">
                <div class="datos_servicio">
                    <hr class="estado_e">
                    <h2>${fila.nombre}</h2>
                    <p>${fila.descripcion}</p>
                    <p>Fecha: ${fila.fecha_transaccion} ${fila.hora_transaccion}</p>
                    <p>Monto: ${fila.monto}</p>
                </div>
                <div class="estado_servicio">
                    <p class="estado_e"><b>${fila.estado}</b></p>
                </div>
            </div>`,
      );
    }
  });
  const contenedorTarjetas = document.getElementById('tarjetas_pago');
  if (contenedorTarjetas) {
    contenedorTarjetas.innerHTML = tarjetasHtml.join('');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (!sesionOk) return;
  cargarTransacciones(`${urlApiTransaccion}read`);
});

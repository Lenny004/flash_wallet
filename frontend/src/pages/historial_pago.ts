/**
 * @file Página de historial de pagos (facturas): listado, búsqueda y eliminación.
 */

import { apiFetchAuth, getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<{ isConfirmed?: boolean }>;
};
declare function sweetAlert(type: 1 | 2 | 3 | 4 | 5, text: string, url?: string | null): void;

const urlApiFactura = `${getApiBase()}/api/factura/`;

/** Fila de factura devuelta por la API. */
interface FilaFactura {
  id_factura: number;
  nombre_servicio: string;
  fecha_factura: string;
  hora_factura: string;
  monto_total: number | string;
}

/** Respuesta genérica de endpoints de factura. */
interface RespuestaFactura {
  estado?: number | boolean;
  dataset?: FilaFactura[];
  mensaje?: string;
  exception?: string;
  message?: string;
  detail?: string;
}

/**
 * Carga el historial de facturas desde la API y lo renderiza en la tabla.
 * @param urlApi - URL completa del endpoint de lectura o búsqueda.
 */
function cargarFacturas(urlApi: string): void {
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
        respuestaApi.json().then((datos: RespuestaFactura) => {
          if (datos.estado === 1) {
            renderizarTabla(datos.dataset ?? []);
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
 * Renderiza las filas de facturas en `#tbfactura`.
 * @param registros - Lista de facturas devueltas por la API.
 */
function renderizarTabla(registros: FilaFactura[]): void {
  const filasHtml: string[] = [];
  registros.forEach((fila) => {
    filasHtml.push(`
            <tr>
                <td>${fila.nombre_servicio}</td>
                <td>${fila.fecha_factura}</td>
                <td>${fila.hora_factura}</td>
                <td>$${fila.monto_total}</td>
                <td>
                    <img onclick="openDelete(${fila.id_factura})" src="/resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
  });
  const cuerpoTabla = document.getElementById('tbfactura');
  if (cuerpoTabla) cuerpoTabla.innerHTML = filasHtml.join('');
}

/**
 * Solicita confirmación y elimina una factura por su ID.
 * @param idFactura - Identificador de la factura a eliminar.
 */
function openDelete(idFactura: number): void {
  Swal.fire({
    title: 'Advertencia',
    text: '¿Desea eliminar el registro?',
    icon: 'warning',
    confirmButtonText: 'Si',
    confirmButtonColor: '#b01e68',
    showCancelButton: true,
    cancelButtonColor: '#6b4a5f',
    cancelButtonText: 'No',
    allowOutsideClick: false,
    allowEscapeKey: false,
    allowEnterKey: true,
    stopKeydownPropagation: false,
  }).then((resultado) => {
    if (resultado.isConfirmed) {
      apiFetchAuth(`${urlApiFactura}delete`, {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_factura: idFactura }),
      }).then((respuestaApi) => {
        if (respuestaApi.ok) {
          respuestaApi.json().then((datos: RespuestaFactura) => {
            if (datos.estado) {
              cargarFacturas(`${urlApiFactura}read`);
              sweetAlert(1, datos.message || 'Registro eliminado', null);
            } else {
              sweetAlert(2, datos.exception || 'Error al eliminar', null);
            }
          });
        } else {
          console.log(`${respuestaApi.status} ${respuestaApi.statusText}`);
        }
      });
    }
  });
}

declare global {
  interface Window {
    openDelete: (id: number) => void;
  }
}

window.openDelete = openDelete;

document.addEventListener('DOMContentLoaded', () => {
  cargarFacturas(`${urlApiFactura}read`);
});

const formularioBuscador = document.getElementById('buscador-form');
formularioBuscador?.addEventListener('submit', (evento) => {
  evento.preventDefault();
  const nombreBusqueda = (document.getElementById('buscar') as HTMLInputElement).value;
  apiFetchAuth(`${urlApiFactura}buscar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre: nombreBusqueda }),
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        throw new Error(errorDatos.detail || 'Error desconocido');
      });
    })
    .then((datos: RespuestaFactura) => {
      if (datos.estado) {
        renderizarTabla(datos.dataset ?? []);
        sweetAlert(1, datos.mensaje || 'Búsqueda exitosa', null);
      } else {
        sweetAlert(4, datos.exception || 'No hay resultados', null);
        cargarFacturas(`${urlApiFactura}read`);
      }
    })
    .catch((error: Error) => {
      sweetAlert(4, error.message, null);
      console.log(error);
      cargarFacturas(`${urlApiFactura}read`);
    });
});

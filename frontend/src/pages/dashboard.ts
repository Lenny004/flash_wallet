/**
 * @file Panel principal (dashboard): historial de recargas, movimientos, datos de tarjeta y búsqueda.
 */

import { apiFetchAuth, getApiBase, requireCardSession } from '../lib/auth';

/** Guard de sesión: requiere token de tarjeta. */
const sesionOk = requireCardSession();

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<{ isConfirmed?: boolean }>;
};

const urlApiHistorial = `${getApiBase()}/api/historial/`;
const urlApiTarjeta = `${getApiBase()}/api/tarjeta/`;
const urlApiMovimientos = `${getApiBase()}/api/historial/movimientos`;

/** Códigos de tipo de alerta SweetAlert usados en la página. */
type TipoAlerta = 1 | 2 | 3 | 4 | 5;

/**
 * Muestra una alerta SweetAlert según el tipo indicado.
 * @param tipoAlerta - 1 éxito, 2 error, 3 advertencia, 4 aviso, 5 campos vacíos.
 * @param texto - Mensaje a mostrar al usuario.
 * @param urlRedireccion - URL opcional; si se indica, redirige al confirmar.
 */
function mostrarAlerta(tipoAlerta: TipoAlerta, texto: string, urlRedireccion?: string | null): void {
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

/** Fila del historial de recargas. */
interface FilaHistorial {
  id_historial: number;
  monto_agregado: number | string;
  fecha_historial: string;
  hora_historial: string;
}

/** Fila del historial de movimientos de la tarjeta. */
interface FilaMovimiento {
  creado_en: string;
  tipo: string;
  monto: number | string;
  saldo_anterior: number | string;
  saldo_nuevo: number | string;
  referencia?: string;
}

/** Respuesta de la API al consultar el historial de recargas. */
interface RespuestaHistorial {
  estado?: number;
  dataset?: FilaHistorial[];
  exception?: string;
  mensaje?: string;
}

/** Respuesta de la API al consultar movimientos. */
interface RespuestaMovimientos {
  estado?: number;
  dataset?: FilaMovimiento[];
  exception?: string;
}

/** Respuesta de la API con datos de la tarjeta. */
interface RespuestaTarjeta {
  estado?: boolean;
  pan?: string;
  fecha_creacion?: string;
  cvc?: string;
  nombre?: string;
  balance?: number | string;
  exception?: string;
  detail?: string;
}

/** Respuesta de la API al eliminar un registro del historial. */
interface RespuestaEliminar {
  estado?: boolean;
  message?: string;
  exception?: string;
}

/**
 * Carga filas del historial de recargas desde la API y las muestra en la tabla.
 * @param urlApi - URL completa del endpoint de lectura o búsqueda.
 */
function cargarHistorial(urlApi: string): void {
  if (!localStorage.getItem('token_tarjeta')) {
    mostrarAlerta(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  apiFetchAuth(urlApi, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        respuestaApi.json().then((datos: RespuestaHistorial) => {
          if (datos.estado === 1) {
            renderizarTablaHistorial(datos.dataset ?? []);
          }
        });
      } else {
        mostrarAlerta(2, respuestaApi.statusText);
      }
    })
    .catch((error: unknown) => {
      mostrarAlerta(4, 'Hubo un problema con la solicitud.', null);
      console.log('Error:', error);
    });
}

/**
 * Renderiza las filas del historial de recargas en `#tbhistorial`.
 * @param registros - Lista de filas devueltas por la API.
 */
function renderizarTablaHistorial(registros: FilaHistorial[]): void {
  const filasHtml: string[] = [];
  registros.forEach((fila) => {
    filasHtml.push(`
            <tr>
                <td>$${fila.monto_agregado}</td>
                <td>${fila.fecha_historial}</td>
                <td>${fila.hora_historial}</td>
                <td>
                    <img onclick="openDelete(${fila.id_historial})" src="/resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
  });
  const cuerpoTabla = document.getElementById('tbhistorial');
  if (cuerpoTabla) {
    cuerpoTabla.innerHTML = filasHtml.join('');
  }
}

/** Carga y muestra el historial de movimientos de la tarjeta. */
function cargarMovimientos(): void {
  const avisoMovimientos = document.getElementById('movimientos-aviso');
  const cuerpoTabla = document.getElementById('tbmovimientos');
  if (!localStorage.getItem('token_tarjeta')) {
    if (avisoMovimientos) {
      avisoMovimientos.hidden = false;
      avisoMovimientos.textContent = 'No se pudieron cargar los movimientos.';
    }
    return;
  }
  apiFetchAuth(urlApiMovimientos, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      throw new Error(respuestaApi.statusText);
    })
    .then((datos: RespuestaMovimientos) => {
      if (datos.estado === 1) {
        renderizarTablaMovimientos(datos.dataset ?? []);
      } else {
        throw new Error(datos.exception || 'No se pudieron cargar los movimientos.');
      }
    })
    .catch((error: unknown) => {
      console.log('Movimientos:', error);
      if (avisoMovimientos) {
        avisoMovimientos.hidden = false;
        avisoMovimientos.textContent = 'No se pudieron cargar los movimientos.';
      }
      if (cuerpoTabla) {
        cuerpoTabla.innerHTML = '';
      }
    });
}

/**
 * Formatea la fecha/hora de un movimiento para mostrar en la tabla.
 * @param fechaCreacion - Timestamp ISO devuelto por la API.
 * @returns Cadena formateada en locale `es-MX` o el valor original si no es válida.
 */
function formatearFechaMovimiento(fechaCreacion: string): string {
  const fecha = new Date(fechaCreacion);
  if (isNaN(fecha.getTime())) {
    return fechaCreacion || '-';
  }
  return fecha.toLocaleString('es-MX', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Formatea un monto numérico como moneda con dos decimales.
 * @param valor - Monto devuelto por la API.
 * @returns Cadena con prefijo `$` y dos decimales.
 */
function formatearMonto(valor: number | string): string {
  return '$' + parseFloat(String(valor)).toFixed(2);
}

/**
 * Renderiza las filas de movimientos en `#tbmovimientos`.
 * @param registros - Lista de movimientos devueltos por la API.
 */
function renderizarTablaMovimientos(registros: FilaMovimiento[]): void {
  const cuerpoTabla = document.getElementById('tbmovimientos');
  if (!cuerpoTabla) {
    return;
  }
  if (!registros || registros.length === 0) {
    cuerpoTabla.innerHTML = '<tr><td colspan="6">No hay movimientos registrados.</td></tr>';
    return;
  }
  const filasHtml: string[] = [];
  registros.forEach((fila) => {
    filasHtml.push(`
            <tr>
                <td>${formatearFechaMovimiento(fila.creado_en)}</td>
                <td>${fila.tipo}</td>
                <td>${formatearMonto(fila.monto)}</td>
                <td>${formatearMonto(fila.saldo_anterior)}</td>
                <td>${formatearMonto(fila.saldo_nuevo)}</td>
                <td>${fila.referencia || '-'}</td>
            </tr>
        `);
  });
  cuerpoTabla.innerHTML = filasHtml.join('');
}

/** Obtiene y muestra los datos de la tarjeta y el saldo del wallet. */
function cargarDatosTarjeta(): void {
  if (!localStorage.getItem('token_tarjeta')) {
    mostrarAlerta(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  apiFetchAuth(`${urlApiTarjeta}readOne`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        console.error('Error en la solicitud:', errorDatos);
        throw new Error(errorDatos.detail || 'Error al cargar los datos.');
      });
    })
    .then((datos: RespuestaTarjeta) => {
      if (datos.estado) {
        const htmlDatosTarjeta = `
                <p><b>${datos.pan}</b></p>
                <p><b>DESDE: ${datos.fecha_creacion}</b></p>
                <p><b>CVC: ${datos.cvc}</b></p>
                <p><b>${datos.nombre}</b></p>`;
        const contenedorTarjeta = document.getElementById('datos_tarjeta');
        if (contenedorTarjeta) {
          contenedorTarjeta.innerHTML = htmlDatosTarjeta;
        }
        const htmlSaldo = `<p>Saldo en tu wallet</p>
            <p>$${parseFloat(String(datos.balance)).toFixed(2)}</p>`;
        const contenedorSaldo = document.getElementById('dato_balance');
        if (contenedorSaldo) {
          contenedorSaldo.innerHTML = htmlSaldo;
        }
      } else {
        mostrarAlerta(3, datos.exception || 'Ocurrió un error.', null);
      }
    })
    .catch((error: Error) => {
      console.error('Error:', error.message);
      mostrarAlerta(3, error.message, 'login.html');
    });
}

declare global {
  interface Window {
    openDelete: (id: number) => void;
  }
}

/**
 * Solicita confirmación y elimina un registro del historial por su ID.
 * @param idHistorial - Identificador del registro a eliminar.
 */
function openDelete(idHistorial: number): void {
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
      apiFetchAuth(`${urlApiHistorial}delete`, {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_historial: idHistorial }),
      }).then((respuestaApi) => {
        if (respuestaApi.ok) {
          respuestaApi.json().then((datos: RespuestaEliminar) => {
            if (datos.estado) {
              cargarHistorial(`${urlApiHistorial}read`);
              mostrarAlerta(1, datos.message || 'Registro eliminado.', null);
            } else {
              cargarHistorial(`${urlApiHistorial}read`);
              mostrarAlerta(2, datos.exception || 'Error al eliminar.', null);
            }
          });
        } else {
          console.log(`${respuestaApi.status} ${respuestaApi.statusText}`);
        }
      });
    }
  });
}

window.openDelete = openDelete;

document.addEventListener('DOMContentLoaded', () => {
  if (!sesionOk) return;
  cargarHistorial(`${urlApiHistorial}read`);
  cargarDatosTarjeta();
  cargarMovimientos();
});

const formularioBuscador = document.getElementById('buscador-form');
formularioBuscador?.addEventListener('submit', (evento) => {
  if (!sesionOk) return;
  evento.preventDefault();
  const monto_agregado = (document.getElementById('buscar') as HTMLInputElement).value;
  apiFetchAuth(`${urlApiHistorial}buscar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ monto_agregado }),
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        throw new Error(errorDatos.detail || 'Error desconocido');
      });
    })
    .then((datos: RespuestaHistorial) => {
      if (datos.estado) {
        renderizarTablaHistorial(datos.dataset ?? []);
        mostrarAlerta(1, datos.mensaje || 'Búsqueda exitosa.', null);
      } else {
        mostrarAlerta(4, datos.exception || 'No hay resultados', null);
        cargarHistorial(`${urlApiHistorial}read`);
      }
    })
    .catch((error: Error) => {
      mostrarAlerta(4, error.message, null);
      console.log(error);
      cargarHistorial(`${urlApiHistorial}read`);
    });
});

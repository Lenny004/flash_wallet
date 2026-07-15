import { apiFetchAuth, getApiBase } from '../lib/auth';

declare const Swal: {
  fire: (options: Record<string, unknown>) => Promise<{ isConfirmed?: boolean }>;
};

const API_HISTORIAL = `${getApiBase()}/api/historial/`;
const API_TARJETA = `${getApiBase()}/api/tarjeta/`;
const API_MOVIMIENTOS = `${getApiBase()}/api/historial/movimientos`;

type AlertType = 1 | 2 | 3 | 4 | 5;

function sweetAlert(type: AlertType, text: string, url?: string | null): void {
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

interface HistorialRow {
  id_historial: number;
  monto_agregado: number | string;
  fecha_historial: string;
  hora_historial: string;
}

interface MovimientoRow {
  creado_en: string;
  tipo: string;
  monto: number | string;
  saldo_anterior: number | string;
  saldo_nuevo: number | string;
  referencia?: string;
}

interface HistorialResponse {
  estado?: number;
  dataset?: HistorialRow[];
  exception?: string;
  mensaje?: string;
}

interface MovimientosResponse {
  estado?: number;
  dataset?: MovimientoRow[];
  exception?: string;
}

interface TarjetaResponse {
  estado?: boolean;
  pan?: string;
  fecha_creacion?: string;
  cvc?: string;
  nombre?: string;
  balance?: number | string;
  exception?: string;
  detail?: string;
}

interface DeleteResponse {
  estado?: boolean;
  message?: string;
  exception?: string;
}

function readRows(api: string): void {
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  apiFetchAuth(api, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((request) => {
      if (request.ok) {
        request.json().then((response: HistorialResponse) => {
          if (response.estado === 1) {
            fillTable(response.dataset ?? []);
          }
        });
      } else {
        sweetAlert(2, request.statusText);
      }
    })
    .catch((error: unknown) => {
      sweetAlert(4, 'Hubo un problema con la solicitud.', null);
      console.log('Error:', error);
    });
}

function fillTable(dataset: HistorialRow[]): void {
  const content: string[] = [];
  dataset.forEach((row) => {
    content.push(`
            <tr>
                <td>$${row.monto_agregado}</td>
                <td>${row.fecha_historial}</td>
                <td>${row.hora_historial}</td>
                <td>
                    <img onclick="openDelete(${row.id_historial})" src="/resources/icons/delete.png" alt="eliminar">
                </td>
            </tr>
        `);
  });
  const tbody = document.getElementById('tbhistorial');
  if (tbody) {
    tbody.innerHTML = content.join('');
  }
}

function loadMovimientos(): void {
  const aviso = document.getElementById('movimientos-aviso');
  const tbody = document.getElementById('tbmovimientos');
  if (!localStorage.getItem('token_tarjeta')) {
    if (aviso) {
      aviso.hidden = false;
      aviso.textContent = 'No se pudieron cargar los movimientos.';
    }
    return;
  }
  apiFetchAuth(API_MOVIMIENTOS, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((request) => {
      if (request.ok) {
        return request.json();
      }
      throw new Error(request.statusText);
    })
    .then((response: MovimientosResponse) => {
      if (response.estado === 1) {
        fillMovimientosTable(response.dataset ?? []);
      } else {
        throw new Error(response.exception || 'No se pudieron cargar los movimientos.');
      }
    })
    .catch((error: unknown) => {
      console.log('Movimientos:', error);
      if (aviso) {
        aviso.hidden = false;
        aviso.textContent = 'No se pudieron cargar los movimientos.';
      }
      if (tbody) {
        tbody.innerHTML = '';
      }
    });
}

function formatFechaMovimiento(creadoEn: string): string {
  const fecha = new Date(creadoEn);
  if (isNaN(fecha.getTime())) {
    return creadoEn || '-';
  }
  return fecha.toLocaleString('es-MX', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatMontoMovimiento(valor: number | string): string {
  return '$' + parseFloat(String(valor)).toFixed(2);
}

function fillMovimientosTable(dataset: MovimientoRow[]): void {
  const tbody = document.getElementById('tbmovimientos');
  if (!tbody) {
    return;
  }
  if (!dataset || dataset.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6">No hay movimientos registrados.</td></tr>';
    return;
  }
  const content: string[] = [];
  dataset.forEach((row) => {
    content.push(`
            <tr>
                <td>${formatFechaMovimiento(row.creado_en)}</td>
                <td>${row.tipo}</td>
                <td>${formatMontoMovimiento(row.monto)}</td>
                <td>${formatMontoMovimiento(row.saldo_anterior)}</td>
                <td>${formatMontoMovimiento(row.saldo_nuevo)}</td>
                <td>${row.referencia || '-'}</td>
            </tr>
        `);
  });
  tbody.innerHTML = content.join('');
}

function datosTarjeta(): void {
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  apiFetchAuth(`${API_TARJETA}readOne`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((request) => {
      if (request.ok) {
        return request.json();
      }
      return request.json().then((error: { detail?: string }) => {
        console.error('Error en la solicitud:', error);
        throw new Error(error.detail || 'Error al cargar los datos.');
      });
    })
    .then((response: TarjetaResponse) => {
      if (response.estado) {
        const content = `
                <p><b>${response.pan}</b></p>
                <p><b>DESDE: ${response.fecha_creacion}</b></p>
                <p><b>CVC: ${response.cvc}</b></p>
                <p><b>${response.nombre}</b></p>`;
        const datosTarjetaEl = document.getElementById('datos_tarjeta');
        if (datosTarjetaEl) {
          datosTarjetaEl.innerHTML = content;
        }
        const content2 = `<p>Saldo en tu wallet</p>
            <p>$${parseFloat(String(response.balance)).toFixed(2)}</p>`;
        const datoBalanceEl = document.getElementById('dato_balance');
        if (datoBalanceEl) {
          datoBalanceEl.innerHTML = content2;
        }
      } else {
        sweetAlert(3, response.exception || 'Ocurrió un error.', null);
      }
    })
    .catch((error: Error) => {
      console.error('Error:', error.message);
      sweetAlert(3, error.message, 'login.html');
    });
}

declare global {
  interface Window {
    openDelete: (id: number) => void;
  }
}

function openDelete(id: number): void {
  const id_historial = id;
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
  }).then((result) => {
    if (result.isConfirmed) {
      apiFetchAuth(`${API_HISTORIAL}delete`, {
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_historial }),
      }).then((request) => {
        if (request.ok) {
          request.json().then((response: DeleteResponse) => {
            if (response.estado) {
              readRows(`${API_HISTORIAL}read`);
              sweetAlert(1, response.message || 'Registro eliminado.', null);
            } else {
              readRows(`${API_HISTORIAL}read`);
              sweetAlert(2, response.exception || 'Error al eliminar.', null);
            }
          });
        } else {
          console.log(`${request.status} ${request.statusText}`);
        }
      });
    }
  });
}

window.openDelete = openDelete;

document.addEventListener('DOMContentLoaded', () => {
  readRows(`${API_HISTORIAL}read`);
  datosTarjeta();
  loadMovimientos();
});

const buscadorForm = document.getElementById('buscador-form');
buscadorForm?.addEventListener('submit', (event) => {
  event.preventDefault();
  const monto_agregado = (document.getElementById('buscar') as HTMLInputElement).value;
  apiFetchAuth(`${API_HISTORIAL}buscar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ monto_agregado }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      return response.json().then((errorData: { detail?: string }) => {
        throw new Error(errorData.detail || 'Error desconocido');
      });
    })
    .then((data: HistorialResponse) => {
      if (data.estado) {
        fillTable(data.dataset ?? []);
        sweetAlert(1, data.mensaje || 'Búsqueda exitosa.', null);
      } else {
        sweetAlert(4, data.exception || 'No hay resultados', null);
        readRows(`${API_HISTORIAL}read`);
      }
    })
    .catch((error: Error) => {
      sweetAlert(4, error.message, null);
      console.log(error);
      readRows(`${API_HISTORIAL}read`);
    });
});

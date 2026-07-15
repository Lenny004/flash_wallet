/**
 * @file Página de escaneo de servicio: decodifica QR y crea transacciones de pago.
 */

import { apiFetchAuth, getApiBase } from '../lib/auth';

declare function sweetAlert(type: 1 | 2 | 3 | 4 | 5, text: string, url?: string | null): void;

const urlApiDecodeQr = `${getApiBase()}/api/decode_qr/`;
const urlApiTransaccion = `${getApiBase()}/api/transaccion/`;

/** Datos firmados extraídos del código QR escaneado. */
interface IntentoQr {
  fecha: string;
  hora: string;
  monto: number;
  frecuencia: number;
  descripcion: string;
  id_servicio: number;
  id_estado: number;
  exp: number;
  sig: string;
}

/** Respuesta del endpoint de decodificación de QR. */
interface RespuestaDecodeQr {
  estado?: number;
  id_servicio?: number;
  intent?: IntentoQr;
  servicio?: { imagen: string; nombre_servicio: string };
  descripcion?: string;
  monto?: number | string;
  fecha?: string;
  hora?: string;
  frecuencia?: number;
  id_estado?: number;
  error?: string;
  detail?: string;
}

/** Respuesta del endpoint de creación de transacción. */
interface RespuestaCrearTransaccion {
  estado?: number;
  mensaje?: string;
  exception?: string;
  detail?: string;
}

/** Intento QR válido pendiente de confirmar en el formulario. */
let intentoQr: IntentoQr | null = null;

/** Limpia el formulario y restablece la vista del servicio al estado inicial. */
function vaciarCampos(): void {
  intentoQr = null;
  const idsCampos = [
    'fecha_transaccion',
    'hora_transaccion',
    'monto',
    'frecuencia',
    'descripcion',
    'id_servicio',
    'id_estado',
  ] as const;
  idsCampos.forEach((idCampo) => {
    const input = document.getElementById(idCampo) as HTMLInputElement | null;
    if (input) input.value = '';
  });
  const contenedorServicio = document.getElementById('info_servicio');
  if (contenedorServicio) {
    contenedorServicio.innerHTML = `
        <img src="/resources/imgs/default.jpg" alt="empresa">
        <div class="caja borde"><p></p></div>
        <div class="caja borde"><p></p></div>
        <div class="caja borde"><p>Costo: </p></div>`;
  }
}

/**
 * Muestra la imagen del QR seleccionada y decodifica su contenido vía API.
 * @param evento - Evento `change` del input de archivo.
 */
function mostrarImagen(evento: Event): void {
  vaciarCampos();
  const entradaArchivo = evento.target as HTMLInputElement;
  const imagenQr = document.getElementById('qrImage') as HTMLImageElement | null;

  if (!entradaArchivo.files?.[0]) return;

  const archivoImagen = entradaArchivo.files[0];

  if (!archivoImagen.type.startsWith('image/')) {
    sweetAlert(4, 'Selecciona un archivo de imagen válido.');
    entradaArchivo.value = '';
    return;
  }

  const lectorArchivo = new FileReader();
  lectorArchivo.onload = (eventoLectura) => {
    if (imagenQr && eventoLectura.target?.result) {
      imagenQr.src = eventoLectura.target.result as string;
      imagenQr.style.display = 'block';
    }
  };
  lectorArchivo.readAsDataURL(archivoImagen);

  const formData = new FormData();
  formData.append('qr_image', archivoImagen);

  fetch(urlApiDecodeQr, {
    method: 'POST',
    body: formData,
  })
    .then((respuestaApi) => {
      if (!respuestaApi.ok) {
        return respuestaApi.json().then((errorDatos: { detail?: string }) => {
          throw new Error(errorDatos.detail || 'Error desconocido');
        });
      }
      return respuestaApi.json();
    })
    .then((datos: RespuestaDecodeQr) => {
      if (datos.estado === 1 || datos.id_servicio) {
        intentoQr = datos.intent ?? null;
        const datosServicio = datos.servicio ?? datos;
        const urlImagenServicio =
          'imagen' in datosServicio && datosServicio.imagen
            ? `${getApiBase()}/api/images/servicios/${datosServicio.imagen}`
            : '/resources/imgs/default.jpg';
        const nombreServicio =
          'nombre_servicio' in datosServicio ? datosServicio.nombre_servicio : '';
        const htmlServicio = `
                        <img src="${urlImagenServicio}" alt="empresa">
                        <div class="caja borde"><p>${nombreServicio}</p></div>
                        <div class="caja borde"><p>${datos.descripcion}</p></div>
                        <div class="caja borde"><p>Costo: ${datos.monto}</p></div>`;
        const contenedorServicio = document.getElementById('info_servicio');
        if (contenedorServicio) contenedorServicio.innerHTML = htmlServicio;

        const asignacionesCampos: [string, string | number | undefined][] = [
          ['fecha_transaccion', datos.fecha],
          ['hora_transaccion', datos.hora],
          ['monto', datos.monto],
          ['frecuencia', datos.frecuencia],
          ['descripcion', datos.descripcion],
          ['id_servicio', datos.id_servicio],
          ['id_estado', datos.id_estado],
        ];
        asignacionesCampos.forEach(([idCampo, valor]) => {
          const input = document.getElementById(idCampo) as HTMLInputElement | null;
          if (input && valor !== undefined) input.value = String(valor);
        });
      } else {
        sweetAlert(2, datos.error || 'Error al decodificar el QR');
      }
    })
    .catch((error: Error) => {
      sweetAlert(2, `Error: ${error.message}`);
    });
}

declare global {
  interface Window {
    mostrarImagen: (event: Event) => void;
    vaciarCampos: () => void;
  }
}

window.mostrarImagen = mostrarImagen;
window.vaciarCampos = vaciarCampos;

const formularioFactura = document.getElementById('factura_form');
formularioFactura?.addEventListener('submit', (evento) => {
  evento.preventDefault();
  if (!localStorage.getItem('token_tarjeta')) {
    sweetAlert(3, 'No hay datos de la tarjeta. Error', null);
    return;
  }
  if (!intentoQr?.sig || !intentoQr?.exp) {
    sweetAlert(4, 'Escanea un QR válido antes de crear la transacción.', null);
    return;
  }

  const fechaTransaccion = intentoQr.fecha.replace(/\//g, '-');
  const cuerpoPeticion = {
    fecha_transaccion: fechaTransaccion,
    hora_transaccion: intentoQr.hora,
    monto: intentoQr.monto,
    frecuencia: intentoQr.frecuencia,
    descripcion: intentoQr.descripcion,
    id_servicio: intentoQr.id_servicio,
    id_estado: intentoQr.id_estado,
    exp: intentoQr.exp,
    sig: intentoQr.sig,
  };

  apiFetchAuth(`${urlApiTransaccion}crear`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cuerpoPeticion),
  })
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        throw new Error(errorDatos.detail || respuestaApi.statusText);
      });
    })
    .then((datos: RespuestaCrearTransaccion) => {
      if (datos.estado === 1) {
        sweetAlert(1, datos.mensaje || 'Servicio agregado', null);
        vaciarCampos();
      } else {
        sweetAlert(4, datos.exception || 'Error desconocido', null);
      }
    })
    .catch((error: Error) => {
      sweetAlert(4, error.message || 'Hubo un problema con la solicitud.', null);
      console.log('Error:', error);
    });
});

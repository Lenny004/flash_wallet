/**
 * @file Página de perfil de usuario: lectura, edición y actualización de datos personales.
 */

import { apiFetchAuth, getApiBase, requireUserSession } from '../lib/auth';

/** Guard de sesión: requiere token de usuario. */
const sesionOk = requireUserSession();

declare function sweetAlert(type: 1 | 2 | 3 | 4 | 5, text: string, url?: string | null): void;

const urlApiUsuarios = `${getApiBase()}/api/usuarios/`;

/** Respuesta de la API con los datos del perfil del usuario. */
interface RespuestaPerfil {
  estado?: boolean;
  nombres?: string;
  apellidos?: string;
  email?: string;
  direccion?: string;
  telefono?: string;
  exception?: string;
  detail?: string;
}

/** Estado del modo edición: 1 deshabilitado, 2 habilitado. */
let modoEdicion = 1;

/**
 * Carga los datos del perfil del usuario autenticado y los rellena en el formulario.
 * Requiere `token_usuario` en localStorage.
 */
function cargarDatos(): void {
  if (!localStorage.getItem('token_usuario')) {
    sweetAlert(3, 'No hay sesión activa. Redirigiendo al login...', 'login.html');
    return;
  }
  apiFetchAuth(`${urlApiUsuarios}readOne`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  }, 'usuario')
    .then((respuestaApi) => {
      if (respuestaApi.ok) {
        return respuestaApi.json();
      }
      return respuestaApi.json().then((errorDatos: { detail?: string }) => {
        console.error('Error en la solicitud:', errorDatos);
        throw new Error(errorDatos.detail || 'Error al cargar los datos.');
      });
    })
    .then((datos: RespuestaPerfil) => {
      if (datos.estado) {
        const camposPerfil: [string, string | undefined][] = [
          ['nombres', datos.nombres],
          ['apellidos', datos.apellidos],
          ['email', datos.email],
          ['direccion', datos.direccion],
          ['telefono', datos.telefono],
        ];
        camposPerfil.forEach(([idCampo, valor]) => {
          const input = document.getElementById(idCampo) as HTMLInputElement | null;
          if (input && valor !== undefined) input.value = valor;
        });
      } else {
        sweetAlert(3, datos.exception || 'Ocurrió un error.', null);
      }
    })
    .catch((error: Error) => {
      console.error('Error:', error.message);
      sweetAlert(3, error.message, 'login.html');
    });
}

/**
 * Alterna la edición de los campos editables del perfil (`.miInput`).
 * Actualiza el texto del botón y los estilos de los inputs.
 */
function habilitarEdit(): void {
  const inputsEditables = document.querySelectorAll<HTMLInputElement>('.miInput');
  const botonEditar = document.querySelector<HTMLElement>('.subrayar');
  if (modoEdicion === 1) {
    sweetAlert(1, 'Se ha habilitado la edición de datos', null);
    if (botonEditar) botonEditar.innerText = 'Deshabilitar Editar ✏️';
    inputsEditables.forEach((input) => {
      input.disabled = false;
      input.style.color = '#9E2D2D';
      input.style.fontWeight = 'bold';
    });
    modoEdicion = 2;
  } else {
    sweetAlert(3, 'Se ha deshabilitado la edición de datos', null);
    if (botonEditar) botonEditar.innerText = 'Habilitar Editar ✏️';
    inputsEditables.forEach((input) => {
      input.disabled = true;
      input.style.color = '#545454';
      input.style.fontWeight = 'normal';
    });
    modoEdicion = 1;
  }
}

declare global {
  interface Window {
    habilitarEdit: () => void;
  }
}

window.habilitarEdit = habilitarEdit;

document.addEventListener('DOMContentLoaded', () => {
  if (!sesionOk) return;
  cargarDatos();
});

const formularioPerfil = document.getElementById('perfil_form');
formularioPerfil?.addEventListener('submit', async (evento) => {
  if (!sesionOk) return;
  evento.preventDefault();

  const botonEnviar = document.getElementById('btnUpdate') as HTMLInputElement;
  botonEnviar.disabled = true;
  botonEnviar.value = 'Actualizando...';

  try {
    const datosFormulario = Object.fromEntries(
      new FormData(evento.target as HTMLFormElement),
    ) as Record<string, string>;

    if (!datosFormulario.email || !datosFormulario.telefono) {
      throw new Error('Por favor, completa los campos obligatorios.');
    }

    const respuestaApi = await apiFetchAuth(`${urlApiUsuarios}update`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosFormulario),
    }, 'usuario');

    const datos = (await respuestaApi.json()) as RespuestaPerfil;
    if (!respuestaApi.ok) {
      throw new Error(datos.detail || 'Ocurrió un error al actualizar el perfil.');
    }
    cargarDatos();
    habilitarEdit();
    sweetAlert(1, 'Perfil actualizado exitosamente.');
  } catch (error) {
    sweetAlert(2, (error as Error).message);
  } finally {
    botonEnviar.disabled = false;
    botonEnviar.value = 'Actualizar';
  }
});

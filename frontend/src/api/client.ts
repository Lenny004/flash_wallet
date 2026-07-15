/**
 * @file Cliente HTTP centralizado con soporte de autenticación y renovación de tokens.
 */

import { refreshAccessTokens } from '../lib/auth';

/** Modo de autenticación para las peticiones a la API. */
export type AuthMode = 'usuario' | 'tarjeta' | 'none';

/** Opciones extendidas de `fetch` con modo de autenticación opcional. */
export interface ApiFetchOptions extends RequestInit {
  auth?: AuthMode;
}

const urlBaseApi = import.meta.env.VITE_API_URL ?? '';

/**
 * Obtiene el token JWT almacenado según el modo de autenticación indicado.
 * @param modoAuth - Modo de autenticación solicitado.
 * @returns Token almacenado o `null` si no aplica auth o no existe el token.
 */
function obtenerToken(modoAuth: AuthMode): string | null {
  if (modoAuth === 'none') {
    return null;
  }

  const claveToken = modoAuth === 'usuario' ? 'token_usuario' : 'token_tarjeta';
  return localStorage.getItem(claveToken);
}

/**
 * Realiza una petición HTTP a la API usando la URL base de Vite.
 * Adjunta el token Bearer si se indica auth y reintenta tras 401 renovando tokens.
 * @param ruta - Path relativo al endpoint (p. ej. `/api/usuarios/login`).
 * @param opciones - Opciones de fetch; `auth` define qué token usar (`'none'` por defecto).
 * @returns Respuesta HTTP de `fetch`.
 */
export async function apiFetch(
  ruta: string,
  opciones: ApiFetchOptions = {},
): Promise<Response> {
  const { auth = 'none', headers: encabezadosIniciales, ...opcionesRestantes } = opciones;
  const encabezados = new Headers(encabezadosIniciales);

  if (auth !== 'none') {
    const token = obtenerToken(auth);
    if (token) {
      encabezados.set('Authorization', `Bearer ${token}`);
    }
  }

  const urlCompleta = `${urlBaseApi}${ruta}`;
  let respuesta = await fetch(urlCompleta, { ...opcionesRestantes, headers: encabezados });

  if (respuesta.status === 401 && auth !== 'none') {
    const refreshExitoso = await refreshAccessTokens();
    if (!refreshExitoso) {
      localStorage.clear();
      window.location.href = '/pages/login.html';
      return respuesta;
    }
    const tokenRenovado = obtenerToken(auth);
    if (tokenRenovado) {
      encabezados.set('Authorization', `Bearer ${tokenRenovado}`);
    } else {
      encabezados.delete('Authorization');
    }
    respuesta = await fetch(urlCompleta, { ...opcionesRestantes, headers: encabezados });
  }

  return respuesta;
}

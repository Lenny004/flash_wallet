/**
 * @file Utilidades de autenticación: URL base, guards de sesión, renovación de tokens y fetch autenticado.
 */

/** Tipo de token JWT a usar en peticiones autenticadas. */
export type AuthType = 'tarjeta' | 'usuario';

/**
 * Obtiene la URL base de la API.
 * Prioriza `FLASH_API_BASE` en `window` (legacy) y luego `VITE_API_URL`.
 * @returns URL base de la API, o cadena vacía si no está configurada.
 */
export function getApiBase(): string {
  if (typeof window !== 'undefined') {
    const baseUrlLegacy = (window as Window & { FLASH_API_BASE?: string }).FLASH_API_BASE;
    if (baseUrlLegacy !== undefined) {
      return baseUrlLegacy || '';
    }
  }
  return import.meta.env.VITE_API_URL ?? '';
}

/** Redirige a login si no hay access token de usuario (páginas autenticadas). */
export function requireUserSession(redirectTo = '/pages/login.html'): boolean {
  if (!localStorage.getItem('token_usuario')) {
    location.href = redirectTo;
    return false;
  }
  return true;
}

/** Redirige a login si no hay token de tarjeta. */
export function requireCardSession(redirectTo = '/pages/login.html'): boolean {
  if (!localStorage.getItem('token_tarjeta')) {
    location.href = redirectTo;
    return false;
  }
  return true;
}

/**
 * Renueva los tokens de acceso usando el refresh token almacenado en localStorage.
 * @returns `true` si el refresh fue exitoso y se guardaron nuevos tokens; `false` en caso contrario.
 */
export async function refreshAccessTokens(): Promise<boolean> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  const urlBaseApi = getApiBase();
  const respuesta = await fetch(`${urlBaseApi}/api/usuarios/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!respuesta.ok) return false;

  const datosTokens = (await respuesta.json()) as {
    token_usuario?: string;
    token_tarjeta?: string;
  };
  if (datosTokens.token_usuario) localStorage.setItem('token_usuario', datosTokens.token_usuario);
  if (datosTokens.token_tarjeta) localStorage.setItem('token_tarjeta', datosTokens.token_tarjeta);
  return true;
}

/**
 * Realiza una petición HTTP autenticada con reintento automático tras respuesta 401.
 * Compatible con `public/controllers/auth.js`.
 * @param url - URL completa del endpoint (no solo el path relativo).
 * @param options - Opciones estándar de `fetch`.
 * @param authType - Tipo de token: `'tarjeta'` (predeterminado) o `'usuario'`.
 * @returns Respuesta HTTP de `fetch`.
 */
export async function apiFetchAuth(
  url: string,
  options: RequestInit = {},
  authType: AuthType = 'tarjeta',
): Promise<Response> {
  const claveToken = authType === 'usuario' ? 'token_usuario' : 'token_tarjeta';
  const encabezados = new Headers(options.headers);
  encabezados.set('Authorization', `Bearer ${localStorage.getItem(claveToken) || ''}`);

  let respuesta = await fetch(url, { ...options, headers: encabezados });

  if (respuesta.status === 401) {
    const refreshExitoso = await refreshAccessTokens();
    if (!refreshExitoso) {
      localStorage.clear();
      window.location.href = 'login.html';
      return respuesta;
    }
    encabezados.set('Authorization', `Bearer ${localStorage.getItem(claveToken) || ''}`);
    respuesta = await fetch(url, { ...options, headers: encabezados });
  }

  return respuesta;
}

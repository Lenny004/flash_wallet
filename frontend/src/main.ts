/**
 * @file Punto de entrada Vite: expone utilidades de auth en `window` para páginas legacy.
 */

import { apiFetchAuth, refreshAccessTokens } from './lib/auth';

/** Referencia a `window` con propiedades legacy añadidas para compatibilidad. */
const ventanaGlobal = window as Window & {
  apiFetchAuth?: typeof apiFetchAuth;
  refreshAccessTokens?: typeof refreshAccessTokens;
};

ventanaGlobal.apiFetchAuth = apiFetchAuth;
ventanaGlobal.refreshAccessTokens = refreshAccessTokens;

console.log('FLASH');
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL ?? '');

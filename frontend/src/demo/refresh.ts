import { refreshAccessTokens } from '../lib/auth';

/**
 * Demo opcional en index.html: confirma que el módulo de auth carga en ES modules.
 * No ejecuta refresh automáticamente; solo expone la función en consola.
 */
if (import.meta.env.DEV) {
  console.log('[Flash ES] auth.ts cargado; refreshAccessTokens disponible');
}

// Permite probar manualmente desde la consola: `window.__flashRefreshDemo()`
(window as any).__flashRefreshDemo = refreshAccessTokens;

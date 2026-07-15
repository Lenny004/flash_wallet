export type AuthType = 'tarjeta' | 'usuario';

/** Base URL de la API: `FLASH_API_BASE` (legacy) o `VITE_API_URL` (módulos ES). */
export function getApiBase(): string {
  if (typeof window !== 'undefined') {
    const legacy = (window as Window & { FLASH_API_BASE?: string }).FLASH_API_BASE;
    if (legacy !== undefined) {
      return legacy || '';
    }
  }
  return import.meta.env.VITE_API_URL ?? '';
}

export async function refreshAccessTokens(): Promise<boolean> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  const base = getApiBase();
  const res = await fetch(`${base}/api/usuarios/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) return false;

  const data = (await res.json()) as {
    token_usuario?: string;
    token_tarjeta?: string;
  };
  if (data.token_usuario) localStorage.setItem('token_usuario', data.token_usuario);
  if (data.token_tarjeta) localStorage.setItem('token_tarjeta', data.token_tarjeta);
  return true;
}

/**
 * Fetch autenticado compatible con `public/controllers/auth.js`.
 * Recibe la URL completa (no solo el path) y reintenta tras refresh en 401.
 */
export async function apiFetchAuth(
  url: string,
  options: RequestInit = {},
  authType: AuthType = 'tarjeta',
): Promise<Response> {
  const key = authType === 'usuario' ? 'token_usuario' : 'token_tarjeta';
  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${localStorage.getItem(key) || ''}`);

  let res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    const ok = await refreshAccessTokens();
    if (!ok) {
      localStorage.clear();
      window.location.href = 'login.html';
      return res;
    }
    headers.set('Authorization', `Bearer ${localStorage.getItem(key) || ''}`);
    res = await fetch(url, { ...options, headers });
  }

  return res;
}

import { refreshAccessTokens } from '../lib/auth';

export type AuthMode = 'usuario' | 'tarjeta' | 'none';

export interface ApiFetchOptions extends RequestInit {
  auth?: AuthMode;
}

const baseUrl = import.meta.env.VITE_API_URL ?? '';

function getToken(auth: AuthMode): string | null {
  if (auth === 'none') {
    return null;
  }

  const key = auth === 'usuario' ? 'token_usuario' : 'token_tarjeta';
  return localStorage.getItem(key);
}

export async function apiFetch(
  path: string,
  options: ApiFetchOptions = {},
): Promise<Response> {
  const { auth = 'none', headers: initHeaders, ...rest } = options;
  const headers = new Headers(initHeaders);

  if (auth !== 'none') {
    const token = getToken(auth);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const url = `${baseUrl}${path}`;
  let res = await fetch(url, { ...rest, headers });

  if (res.status === 401 && auth !== 'none') {
    const ok = await refreshAccessTokens();
    if (!ok) {
      localStorage.clear();
      window.location.href = '/pages/login.html';
      return res;
    }
    const token = getToken(auth);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    } else {
      headers.delete('Authorization');
    }
    res = await fetch(url, { ...rest, headers });
  }

  return res;
}

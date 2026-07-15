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

async function refreshAccessTokens(): Promise<boolean> {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  const res = await fetch(`${baseUrl}/api/usuarios/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!res.ok) return false;

  const data = await res.json();
  if (data.token_usuario) localStorage.setItem('token_usuario', data.token_usuario);
  if (data.token_tarjeta) localStorage.setItem('token_tarjeta', data.token_tarjeta);
  return true;
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

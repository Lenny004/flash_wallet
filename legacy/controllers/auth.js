/** Invalida el refresh token en el servidor (sin esperar respuesta). */
function revokeRefreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return;
  const base = window.FLASH_API_BASE || '';
  fetch(base + '/api/usuarios/logout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  }).catch(() => {});
}

/**
 * Renueva token_usuario y token_tarjeta con el refresh_token guardado.
 * @returns {Promise<boolean>} true si el refresh fue exitoso
 */
async function refreshAccessTokens() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  const base = window.FLASH_API_BASE || '';
  const res = await fetch(base + '/api/usuarios/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  });
  if (!res.ok) return false;
  const data = await res.json();
  if (data.token_usuario) localStorage.setItem('token_usuario', data.token_usuario);
  if (data.token_tarjeta) localStorage.setItem('token_tarjeta', data.token_tarjeta);
  return true;
}

/**
 * fetch autenticado; reintenta tras renovar tokens si recibe 401.
 * @param {string} url
 * @param {RequestInit} [options]
 * @param {'tarjeta'|'usuario'} [authType]
 * @returns {Promise<Response>}
 */
async function apiFetchAuth(url, options = {}, authType = 'tarjeta') {
  const key = authType === 'usuario' ? 'token_usuario' : 'token_tarjeta';
  options.headers = options.headers || {};
  options.headers['Authorization'] = `Bearer ${localStorage.getItem(key) || ''}`;
  let res = await fetch(url, options);
  if (res.status === 401) {
    const ok = await refreshAccessTokens();
    if (!ok) {
      localStorage.clear();
      location.href = 'login.html';
      return res;
    }
    options.headers['Authorization'] = `Bearer ${localStorage.getItem(key) || ''}`;
    res = await fetch(url, options);
  }
  return res;
}

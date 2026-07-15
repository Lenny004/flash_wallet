import { apiFetchAuth, refreshAccessTokens } from './lib/auth';

// Bridge temporal hacia páginas legacy en public/ (solo disponible donde se carga main.ts).
const w = window as any;
w.apiFetchAuth = apiFetchAuth;
w.refreshAccessTokens = refreshAccessTokens;

console.log('FLASH');
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL ?? '');

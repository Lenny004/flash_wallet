import { defineConfig } from 'vite';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('.', import.meta.url));

export default defineConfig({
  root: '.',
  publicDir: 'public',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(root, 'index.html'),
        login: resolve(root, 'pages/login.html'),
        registro: resolve(root, 'pages/registro.html'),
        dashboard: resolve(root, 'pages/dashboard.html'),
        pago: resolve(root, 'pages/pago.html'),
        recarga: resolve(root, 'pages/recarga.html'),
        escanear_servicio: resolve(root, 'pages/escanear_servicio.html'),
        perfil: resolve(root, 'pages/perfil.html'),
        historial_pago: resolve(root, 'pages/historial_pago.html'),
        tarjeta_digital: resolve(root, 'pages/tarjeta_digital.html'),
      },
    },
  },
});

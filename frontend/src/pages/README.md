# Páginas — migración a módulos ES

Las vistas HTML viven hoy en `public/pages/` y cargan scripts globales desde `public/controllers/`. **No se migran todas a la vez** para no romper dependencias entre `<script>` sin `type="module"`.

## Piloto: `login` (migrado)

La página de login es el **piloto** de la migración a módulos ES con Vite multi-page.

| Recurso | Ubicación nueva | Legacy (aún presente) |
|---------|-----------------|------------------------|
| HTML entry Vite | `pages/login.html` | `public/pages/login.html` |
| Lógica | `src/pages/login.ts` | `public/controllers/login.js` |

- URL en dev: `http://localhost:5173/pages/login.html`
- El HTML carga `<script type="module" src="/src/pages/login.ts">` y SweetAlert2 desde `/resources/js/sweetalert2.all.min.js`.
- La lógica usa `getApiBase()` de `src/lib/auth.ts` para las peticiones públicas (`GET /api/usuarios/`, `POST .../login`). **No** usa `apiFetchAuth` (login es público).
- Guarda `token_usuario`, `token_tarjeta` y `refresh_token` en `localStorage`.
- `vite.config.ts` declara `pages/login.html` en `build.rollupOptions.input` junto con `index.html`.

Cuando el piloto esté validado en dev y build, se podrá deprecar `public/pages/login.html` y `public/controllers/login.js`.

## Estado actual

| Página | Scripts legacy | Migrada a ES |
|--------|----------------|--------------|
| `login.html` | `config.js`, `login.js`, … | **Sí (piloto)** |
| `dashboard.html` | `auth.js`, `dashboard.js`, … | No |
| … | … | No |

## Cómo migrar una página (siguiente)

1. Crear `src/pages/<nombre>.ts` con la lógica del controlador correspondiente (`public/controllers/<nombre>.js`).
2. Crear `pages/<nombre>.html` en la raíz de `frontend/` (entry Vite multi-page), copiando estructura de `public/pages/<nombre>.html` y sustituyendo scripts por:
   ```html
   <script type="module" src="/src/pages/<nombre>.ts"></script>
   ```
3. Añadir la entrada en `vite.config.ts` → `build.rollupOptions.input`.
4. Importar desde `src/lib/auth.ts` (`getApiBase`, `apiFetchAuth`, `refreshAccessTokens`) según corresponda.
5. Probar login, refresh de token y redirección en 401 antes de dar la página por migrada.
6. Mantener `public/pages/<nombre>.html` y `public/controllers/<nombre>.js` hasta confirmar; luego deprecar.

## Orden sugerido

1. Páginas sin auth (`login.html` ✓, `registro.html`)
2. Páginas con `auth.js` (`dashboard.html`, `perfil.html`, …)
3. Eliminar `public/controllers/auth.js` cuando ninguna página lo referencie

## Limitación del bridge global

`src/main.ts` expone `window.apiFetchAuth` y `window.refreshAccessTokens`, pero **solo en `index.html`** (entrada Vite). Las páginas en `/pages/*.html` no cargan `main.ts`; deben importar `src/lib/auth.ts` directamente al migrarse.

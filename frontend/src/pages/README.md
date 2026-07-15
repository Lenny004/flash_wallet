# Páginas — migración a módulos ES

Las vistas HTML viven hoy en `public/pages/` y cargan scripts globales desde `public/controllers/`. **No se migran todas a la vez** para no romper dependencias entre `<script>` sin `type="module"`.

## Estado actual

| Página | Scripts legacy | Migrada a ES |
|--------|----------------|--------------|
| `login.html` | `config.js`, `login.js`, … | No |
| `dashboard.html` | `auth.js`, `dashboard.js`, … | No |
| … | … | No |

## Cómo migrar una página (cuando toque)

1. Crear `src/pages/<nombre>.ts` con la lógica del controlador correspondiente (`public/controllers/<nombre>.js`).
2. En el HTML de la página, sustituir los `<script src="/controllers/...">` por un único:
   ```html
   <script type="module" src="/src/pages/<nombre>.ts"></script>
   ```
3. Importar desde `src/lib/auth.ts` (`apiFetchAuth`, `refreshAccessTokens`) en lugar de depender de `auth.js` global.
4. Probar login, refresh de token y redirección en 401 antes de dar la página por migrada.
5. Mantener `public/controllers/<nombre>.js` hasta confirmar que la página nueva funciona; luego deprecar.

## Orden sugerido

1. Páginas sin auth (`login.html`, `registro.html`)
2. Páginas con `auth.js` (`dashboard.html`, `perfil.html`, …)
3. Eliminar `public/controllers/auth.js` cuando ninguna página lo referencie

## Limitación del bridge global

`src/main.ts` expone `window.apiFetchAuth` y `window.refreshAccessTokens`, pero **solo en `index.html`** (entrada Vite). Las páginas en `/pages/*.html` no cargan `main.ts`; deben importar `src/lib/auth.ts` directamente al migrarse.

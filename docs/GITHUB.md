# Publicación en GitHub

## Metadatos del repositorio

- **Nombre:** `flash-wallet` (o `Flash`).
- **Descripción:** `Billetera digital con tarjeta virtual, pagos QR de servicios, recargas y facturacion - FastAPI + MySQL`.
- **Topics:** `fastapi`, `digital-wallet`, `qr-payments`, `fintech`, `sqlalchemy`, `mysql`, `docker`, `python`.
- **Rama por defecto:** `main` (protegida).
- **Licencia:** MIT.

## Antes del primer push (obligatorio)

1. **Rotar `SECRET_KEY`** y moverla a `.env` (ver [SEGURIDAD.md](SEGURIDAD.md)). La clave actual
   está comprometida por haber estado en el código.
2. Mover `DATABASE_URL` a `.env`.
3. Confirmar que `.gitignore` excluye `.env`, `__pycache__/`, `venv/`, `node_modules/`.
4. Corregir el bug de sintaxis en [dbflash.sql](../dbflash.sql) (coma tras `cvc`).
5. Verificar que ningún archivo con secretos entra en el commit inicial.

## Archivos de repositorio

| Archivo | Estado |
|---------|--------|
| `README.md` (raíz) | A crear (Fase 0) |
| `.gitignore` | A crear (Fase 0) |
| `.env.example` | A crear (Fase 0) |
| `LICENSE` (MIT) | A crear (Fase 0) |
| `CONTRIBUTING.md` | A crear (Fase 1) |
| `docs/` | Creado |
| `.github/workflows/ci.yml` | A crear (Fase 3) |

## Pasos para crear el repositorio

> Ejecutar solo cuando se confirme explícitamente. Requiere `git` y `gh` (GitHub CLI) autenticado.

```bash
# 1. Inicializar git (si no existe)
git init
git branch -M main

# 2. Verificar que no hay secretos rastreados
git status
git add .
git status   # revisar que .env NO aparece

# 3. Primer commit
git commit -m "chore: initial commit - Flash wallet + docs"

# 4. Crear el repo remoto y subir (publico por defecto)

# 5. Añadir topics
gh repo edit --add-topic fastapi,digital-wallet,qr-payments,fintech,sqlalchemy,mysql,docker,python
```

Para hacerlo público más adelante:

```bash
gh repo edit --visibility public
```

## Protección de rama

Una vez con CI activo:

```bash
gh api repos/:owner/flash-wallet/branches/main/protection \
  -X PUT -F required_status_checks.strict=true
```

O configurarlo desde Settings > Branches: requerir PR y checks de CI en verde antes de merge.

## CI mínimo (GitHub Actions)

`.github/workflows/ci.yml` (Fase 3): en cada push/PR instala dependencias, corre `ruff` y
`pytest` en el backend y `npm run build` en el frontend. Ejemplo resumido:

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: ruff check backend
      - run: pytest backend
```

## Convención de commits y ramas

- Ramas: `feature/<nombre>`, `fix/<nombre>`, `chore/<nombre>`.
- Commits: estilo convencional (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
- Versionado semántico con tags (`v0.1.0`, `v0.2.0`, ...).

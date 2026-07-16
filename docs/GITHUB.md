# Publicación en GitHub

## Metadatos del repositorio

- **URL:** https://github.com/Lenny004/flash_wallet
- **Nombre:** `flash_wallet`
- **Descripción:** `Billetera digital con tarjeta virtual, pagos QR de servicios, recargas y facturacion - FastAPI + MySQL`
- **Topics:** `fastapi`, `digital-wallet`, `qr-payments`, `fintech`, `sqlalchemy`, `mysql`, `docker`, `python`
- **Rama base:** `main` — releases estables; protegida, sin push directo.
- **Rama de trabajo:** `develop` — integración y desarrollo diario.
- **Rama por defecto recomendada:** `develop` (trabajo diario) o `main` si prefieres que los clones partan de producción; en ambos casos los cambios llegan a `main` solo vía PR.
- **Licencia:** MIT

## Flujo de ramas

Existen dos ramas permanentes:

| Rama | Rol |
|------|-----|
| `main` | Base / producción — solo merges de release |
| `develop` | Trabajo e integración continua |

- Todo el trabajo va en `develop` o en ramas derivadas (`feature/*`, `fix/*`, `chore/*`).
- **No subir directamente a `main`.** Los cambios llegan a `main` solo vía PR (release).
- Push diario a `origin/develop`.

### PR `develop` → `main` (release)

1. Asegúrate de que `develop` está actualizada y los checks pasan.
2. Abre el compare en GitHub: [main...develop](https://github.com/Lenny004/flash_wallet/compare/main...develop?expand=1)
3. Crea el PR, revisa y mergea cuando corresponda un release.

Con CLI (requiere `gh auth login` antes):

```bash
gh auth login
gh pr create --base main --head develop --title "release: vX.Y.Z" --body "Release desde develop"
```

## Antes del primer push (obligatorio)

1. **Rotar `SECRET_KEY`** y moverla a `.env` (ver [SEGURIDAD.md](SEGURIDAD.md)). Hecho: clave nueva en `.env` local.
2. Mover `DATABASE_URL` a `.env`. Hecho.
3. Confirmar que `.gitignore` excluye `.env`, `__pycache__/`, `venv/`, `node_modules/`.
4. Corregir el bug de sintaxis en [dbflash.sql](../dbflash.sql) (coma tras `cvc`). Hecho.
5. Verificar que ningún archivo con secretos entra en el commit inicial.

## Archivos de repositorio

| Archivo | Estado |
|---------|--------|
| `README.md` (raíz) | Creado |
| `.gitignore` | Creado |
| `.env.example` | Creado |
| `LICENSE` (MIT) | Creado |
| `requirements.txt` | Creado |
| `CONTRIBUTING.md` | A crear (Fase 1) |
| `docs/` | Creado |
| `.github/workflows/ci.yml` | A crear (Fase 3) |

## Comandos git / gh (referencia)

> Requiere `git` y `gh` (GitHub CLI). Si `gh` falla con error de autenticación, ejecuta `gh auth login` una vez.

```bash
# Clonar (si partes de cero)
git clone https://github.com/Lenny004/flash_wallet.git
cd flash_wallet
git checkout develop

# Inicializar git local (solo si el proyecto aún no tiene repo)
git init
git checkout -b develop

# Verificar que no hay secretos rastreados
git status
git add .
git status   # revisar que .env NO aparece

# Primer commit
git commit -m "chore: initial commit - Flash wallet + docs"

# Remoto y push inicial a develop (NO a main)
git remote add origin https://github.com/Lenny004/flash_wallet.git
git push -u origin develop

# Añadir topics al repo remoto
gh repo edit Lenny004/flash_wallet --add-topic fastapi,digital-wallet,qr-payments,fintech,sqlalchemy,mysql,docker,python
```

Para hacerlo público más adelante:

```bash
gh repo edit Lenny004/flash_wallet --visibility public
```

## Protección de rama

Una vez con CI activo:

```bash
gh api repos/Lenny004/flash_wallet/branches/main/protection \
  -X PUT -F required_status_checks.strict=true
```

O configurarlo desde Settings > Branches: requerir PR y checks de CI en verde antes de merge a `main`.

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

- Ramas: `develop` (integración), `feature/<nombre>`, `fix/<nombre>`, `chore/<nombre>`.
- Commits: estilo convencional (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`).
- Versionado semántico con tags (`v0.1.0`, `v0.2.0`, ...).

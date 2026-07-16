# Contribuir a Flash

Gracias por colaborar. Flash está en proceso de profesionalización; sigue estas
convenciones para mantener el repo ordenado.

## Ramas y flujo

| Rama | Uso |
|------|-----|
| `develop` | Integración y trabajo diario |
| `feature/*`, `fix/*`, `chore/*` | Ramas cortas desde `develop` |
| `main` | Releases estables — **sin push directo** |

1. Crea tu rama desde `develop` (`feature/mi-cambio`, etc.).
2. Haz PR hacia `develop` e integra ahí.
3. Para un **release**, abre PR `develop` → `main`: [compare en GitHub](https://github.com/Lenny004/flash_wallet/compare/main...develop?expand=1).

Detalle de comandos y `gh auth login` en [docs/GITHUB.md](docs/GITHUB.md).

## Commits (gitmoji)

Usa gitmoji al inicio del mensaje:

| Emoji | Uso |
|-------|-----|
| ✨ `:sparkles:` | Nueva funcionalidad |
| 🐛 `:bug:` | Corrección de bug |
| 📝 `:memo:` | Documentación |
| ♻️ `:recycle:` | Refactor |
| ✅ `:white_check_mark:` | Tests |
| 🔧 `:wrench:` | Config / tooling |
| 🚀 `:rocket:` | Deploy / release |

Ejemplo: `✨ feat(auth): refresh tokens en login`

## Entorno local

1. Clona el repo y cambia a `develop`.
2. Copia `.env.example` → `.env` y configura `SECRET_KEY` y `DATABASE_URL`.
3. Importa `dbflash.sql` en MySQL.

### Backend

```bash
cd backend
pip install -r ../requirements.txt
uvicorn app.main:app --reload
```

### Frontend (Vite)

```bash
cd frontend
npm install
npm run dev
```

## Tests y lint

Desde la raíz del repo (como en CI):

```bash
pip install -r requirements.txt
ruff check backend/app
cd backend && pytest -q
```

Los tests de humo no requieren MySQL; define `SECRET_KEY` en el entorno (ver `.env.example`).

Frontend:

```bash
cd frontend && npm run build
```

## Dónde escribir código

- **Backend activo:** `backend/app/` — no añadas lógica nueva en `legacy/` (archivo histórico, ver [legacy/README.md](../legacy/README.md)).
- **Frontend activo:** `frontend/`.

Más contexto en [docs/GITHUB.md](docs/GITHUB.md) y [docs/ROADMAP.md](docs/ROADMAP.md).

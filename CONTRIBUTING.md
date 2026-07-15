# Contribuir a Flash

Gracias por colaborar. Flash está en proceso de profesionalización; sigue estas
convenciones para mantener el repo ordenado.

## Ramas

- **`develop`** — rama de integración y trabajo diario.
- **`feature/<nombre>`**, **`fix/<nombre>`**, **`chore/<nombre>`** — ramas cortas desde `develop`.
- **`main`** — solo releases estables vía pull request. **No hagas push directo a `main`.**

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

- **Backend activo:** `backend/app/` — no añadas lógica nueva en `api/` (legacy, ver `api/DEPRECATED.md`).
- **Frontend activo:** `frontend/`.

Más contexto en [docs/GITHUB.md](docs/GITHUB.md) y [docs/ROADMAP.md](docs/ROADMAP.md).

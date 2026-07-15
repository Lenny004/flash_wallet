"""Verifica que SECRET_KEY y DATABASE_URL estén definidos (sin imprimir valores)."""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"

REQUIRED = ("SECRET_KEY", "DATABASE_URL")


def _load_env_file() -> None:
    """Carga variables del .env al entorno si aún no están definidas."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()


def main() -> int:
    """Comprueba variables requeridas; retorna 0 si están presentes, 1 si faltan."""
    _load_env_file()
    missing = [name for name in REQUIRED if not os.environ.get(name, "").strip()]
    if missing:
        print(f"Faltan variables de entorno: {', '.join(missing)}")
        return 1
    print("SECRET_KEY y DATABASE_URL definidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Motor SQLAlchemy y dependencia de sesión para FastAPI."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# --- Motor y fábrica de sesiones ---

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependencia FastAPI que entrega una sesión y la cierra al finalizar.

    Yields:
        Sesión SQLAlchemy vinculada al motor configurado.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

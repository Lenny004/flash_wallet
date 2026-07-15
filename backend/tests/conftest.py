"""Fixtures compartidas para tests de la API Flash."""

import os

# Variables mínimas antes de importar app (Settings exige secret_key).
# SQLAlchemy create_engine() no abre conexión hasta el primer uso; si el import
# falla por otro motivo de DB, revisar session.py y dependencias de modelos.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("DATABASE_URL", "mysql+pymysql://root@localhost/dbflash_test")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)

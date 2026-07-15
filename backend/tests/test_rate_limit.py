"""Tests del rate limiter en memoria."""

import pytest
from fastapi import HTTPException

from app.core import rate_limit as rl


@pytest.fixture(autouse=True)
def clear_hits():
    rl._hits.clear()
    yield
    rl._hits.clear()


def test_rate_limit_permite_hasta_el_limite():
    for _ in range(5):
        rl.rate_limit("test:key", limit=5, window=60)


def test_rate_limit_rechaza_sobre_el_limite():
    for _ in range(5):
        rl.rate_limit("test:key", limit=5, window=60)

    with pytest.raises(HTTPException) as exc:
        rl.rate_limit("test:key", limit=5, window=60)

    assert exc.value.status_code == 429
    assert exc.value.detail == "Demasiadas solicitudes. Intenta más tarde."

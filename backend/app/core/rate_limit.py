"""Rate limiting en memoria por clave (ventana deslizante)."""

from collections import defaultdict
from time import time

from fastapi import HTTPException

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(key: str, limit: int = 10, window: int = 60):
    """Registra una solicitud y rechaza si se supera el límite en la ventana.

    Args:
        key: Identificador del cliente o endpoint (p. ej. IP + ruta).
        limit: Máximo de solicitudes permitidas en la ventana.
        window: Duración de la ventana en segundos.

    Raises:
        HTTPException: 429 si se excede el límite.
    """
    ahora = time()
    timestamps = _hits[key]
    _hits[key] = [marca_tiempo for marca_tiempo in timestamps if ahora - marca_tiempo < window]
    if len(_hits[key]) >= limit:
        raise HTTPException(429, detail="Demasiadas solicitudes. Intenta más tarde.")
    _hits[key].append(ahora)

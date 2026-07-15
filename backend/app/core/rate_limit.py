from collections import defaultdict
from time import time

from fastapi import HTTPException

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(key: str, limit: int = 10, window: int = 60):
    now = time()
    hits = _hits[key]
    _hits[key] = [t for t in hits if now - t < window]
    if len(_hits[key]) >= limit:
        raise HTTPException(429, detail="Demasiadas solicitudes. Intenta más tarde.")
    _hits[key].append(now)

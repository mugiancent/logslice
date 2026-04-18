"""Sampling utilities for log records."""
from __future__ import annotations

import hashlib
from typing import Iterable, Iterator


def sample_every_nth(records: Iterable[dict], n: int) -> Iterator[dict]:
    """Yield every nth record (1-based)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    for i, record in enumerate(records):
        if i % n == 0:
            yield record


def sample_by_rate(records: Iterable[dict], rate: float) -> Iterator[dict]:
    """Yield records where rate is between 0.0 and 1.0 (inclusive)."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be between 0.0 and 1.0, got {rate}")
    if rate == 0.0:
        return
    for record in records:
        if _hash_fraction(record) < rate:
            yield record


def sample_reservoir(records: Iterable[dict], k: int) -> list[dict]:
    """Return a reservoir sample of up to k records."""
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")
    import random
    reservoir: list[dict] = []
    for i, record in enumerate(records):
        if i < k:
            reservoir.append(record)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = record
    return reservoir


def _hash_fraction(record: dict) -> float:
    """Return a stable float in [0, 1) derived from the record's content."""
    raw = str(sorted(record.items())).encode()
    digest = hashlib.md5(raw).hexdigest()[:8]
    return int(digest, 16) / 0xFFFFFFFF

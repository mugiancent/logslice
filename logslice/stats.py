"""Numeric statistics over a numeric field across log records."""
from typing import Iterable, Dict, Any, Optional
import math


def _collect(records: Iterable[Dict[str, Any]], field: str):
    values = []
    for r in records:
        v = r.get(field)
        if v is None:
            continue
        try:
            values.append(float(v))
        except (TypeError, ValueError):
            continue
    return values


def field_stats(records: Iterable[Dict[str, Any]], field: str) -> Optional[Dict[str, float]]:
    """Return min, max, mean, and stddev for *field*. Returns None if no numeric values found."""
    values = _collect(records, field)
    if not values:
        return None
    n = len(values)
    total = sum(values)
    mean = total / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return {
        "count": float(n),
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "stddev": math.sqrt(variance),
    }


def percentile(records: Iterable[Dict[str, Any]], field: str, p: float) -> Optional[float]:
    """Return the p-th percentile (0-100) of *field* values."""
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    values = sorted(_collect(records, field))
    if not values:
        return None
    idx = (p / 100) * (len(values) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (idx - lo)

"""Bucket records into discrete value-based or numeric range bins."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

Record = Dict[str, Any]


def bucket_by_value(records: Iterable[Record], field: str) -> Dict[str, List[Record]]:
    """Group records into buckets keyed by the exact value of *field*."""
    buckets: Dict[str, List[Record]] = {}
    for record in records:
        key = str(record.get(field, ""))
        buckets.setdefault(key, []).append(record)
    return buckets


def bucket_by_range(
    records: Iterable[Record],
    field: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
) -> Dict[str, List[Record]]:
    """Bin numeric *field* values into ranges defined by *edges*.

    *edges* must be sorted ascending.  The resulting buckets are:
      (-inf, edges[0]), [edges[0], edges[1]), ..., [edges[-1], +inf)

    If *labels* is provided it must have ``len(edges) + 1`` entries.
    """
    if labels is not None and len(labels) != len(edges) + 1:
        raise ValueError(
            f"labels length ({len(labels)}) must be len(edges)+1 ({len(edges) + 1})"
        )

    def _label(i: int) -> str:
        if labels:
            return labels[i]
        lo = "-inf" if i == 0 else str(edges[i - 1])
        hi = "+inf" if i == len(edges) else str(edges[i])
        return f"[{lo},{hi})"

    def _bin(value: float) -> str:
        for i, edge in enumerate(edges):
            if value < edge:
                return _label(i)
        return _label(len(edges))

    buckets: Dict[str, List[Record]] = {_label(i): [] for i in range(len(edges) + 1)}
    for record in records:
        raw = record.get(field)
        try:
            value = float(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        buckets[_bin(value)].append(record)
    return buckets


def bucket_counts(buckets: Dict[str, List[Record]]) -> Dict[str, int]:
    """Return a mapping of bucket label -> record count."""
    return {k: len(v) for k, v in buckets.items()}


def top_buckets(
    buckets: Dict[str, List[Record]], n: int = 5
) -> List[Tuple[str, int]]:
    """Return the *n* largest buckets as (label, count) pairs, descending."""
    counts = bucket_counts(buckets)
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

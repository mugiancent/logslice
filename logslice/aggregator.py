"""Simple aggregation helpers for grouped log records."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional


def group_by(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group records by the value of *field*.

    Records that do not contain *field* are grouped under the empty-string key.
    """
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = str(record.get(field, ""))
        groups[key].append(record)
    return dict(groups)


def count_by(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Return a mapping of field-value -> occurrence count."""
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        key = str(record.get(field, ""))
        counts[key] += 1
    return dict(counts)


def top_n(records: Iterable[Dict[str, Any]], field: str, n: int = 10) -> List[Dict[str, Any]]:
    """Return the *n* most common values of *field* with their counts.

    Each entry in the returned list is a dict with keys ``value`` and ``count``,
    sorted descending by count.
    """
    if n <= 0:
        raise ValueError(f"n must be a positive integer, got {n!r}")
    counts = count_by(records, field)
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    return [{"value": value, "count": count} for value, count in sorted_counts[:n]]


def summarise(
    records: Iterable[Dict[str, Any]],
    group_field: str,
    numeric_field: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return one summary dict per unique value of *group_field*.

    Each summary contains:
      - ``group_field``: the group value
      - ``count``: number of records in the group
      - ``sum``, ``min``, ``max`` (only when *numeric_field* is provided and
        at least one record has a numeric value for it)
    """
    groups = group_by(records, group_field)
    result: List[Dict[str, Any]] = []
    for key, group_records in sorted(groups.items()):
        entry: Dict[str, Any] = {group_field: key, "count": len(group_records)}
        if numeric_field is not None:
            values = []
            for r in group_records:
                try:
                    values.append(float(r[numeric_field]))
                except (KeyError, TypeError, ValueError):
                    pass
            if values:
                entry["sum"] = sum(values)
                entry["min"] = min(values)
                entry["max"] = max(values)
        result.append(entry)
    return result

"""Field type casting utilities for logslice records."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional


_MISSING = object()


def cast_field(
    record: Dict[str, Any],
    field: str,
    target_type: type,
    default: Any = _MISSING,
) -> Dict[str, Any]:
    """Return a copy of *record* with *field* cast to *target_type*.

    If the field is absent the record is returned unchanged.
    If casting fails and *default* is provided that value is used;
    otherwise the original value is preserved.
    """
    if field not in record:
        return dict(record)
    result = dict(record)
    try:
        result[field] = target_type(record[field])
    except (ValueError, TypeError):
        if default is not _MISSING:
            result[field] = default
        # else leave original value intact
    return result


def cast_fields(
    record: Dict[str, Any],
    cast_map: Dict[str, type],
) -> Dict[str, Any]:
    """Apply multiple casts described by *cast_map* ``{field: type}``."""
    result = dict(record)
    for field, target_type in cast_map.items():
        result = cast_field(result, field, target_type)
    return result


def apply_casts(
    records: Iterable[Dict[str, Any]],
    cast_map: Dict[str, type],
) -> List[Dict[str, Any]]:
    """Apply *cast_map* to every record in *records*."""
    return [cast_fields(r, cast_map) for r in records]


def safe_int(value: Any, default: int = 0) -> int:
    """Convert *value* to int, returning *default* on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert *value* to float, returning *default* on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

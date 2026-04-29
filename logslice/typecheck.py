"""Type-checking utilities for log records.

Provides functions to assert or test field types across records,
and to partition records into passing/failing sets.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple

_TYPE_MAP: Dict[str, type] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def _resolve_type(t: str | type) -> type:
    """Accept a type object or a string name and return a type."""
    if isinstance(t, type):
        return t
    try:
        return _TYPE_MAP[t]
    except KeyError:
        raise ValueError(f"Unknown type name: {t!r}")


def check_field_type(record: Dict[str, Any], field: str, expected: str | type) -> bool:
    """Return True if *field* is present and its value is an instance of *expected*."""
    if field not in record:
        return False
    return isinstance(record[field], _resolve_type(expected))


def check_fields_types(
    record: Dict[str, Any], spec: Dict[str, str | type]
) -> Dict[str, bool]:
    """Check multiple fields at once.

    Returns a mapping of field name -> bool indicating whether each
    field passes its type check.
    """
    return {field: check_field_type(record, field, t) for field, t in spec.items()}


def filter_by_type(
    records: Iterable[Dict[str, Any]],
    field: str,
    expected: str | type,
) -> Iterator[Dict[str, Any]]:
    """Yield only records where *field* matches *expected* type."""
    t = _resolve_type(expected)
    for record in records:
        if isinstance(record.get(field), t):
            yield record


def partition_by_type(
    records: Iterable[Dict[str, Any]],
    field: str,
    expected: str | type,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split records into (passing, failing) based on *field* type check."""
    t = _resolve_type(expected)
    passing: List[Dict[str, Any]] = []
    failing: List[Dict[str, Any]] = []
    for record in records:
        if isinstance(record.get(field), t):
            passing.append(record)
        else:
            failing.append(record)
    return passing, failing


def type_errors(
    record: Dict[str, Any], spec: Dict[str, str | type]
) -> List[str]:
    """Return a list of human-readable error strings for fields that fail their type check."""
    errors: List[str] = []
    for field, expected in spec.items():
        t = _resolve_type(expected)
        if field not in record:
            errors.append(f"field {field!r} is missing")
        elif not isinstance(record[field], t):
            actual = type(record[field]).__name__
            errors.append(
                f"field {field!r} expected {t.__name__} but got {actual}"
            )
    return errors

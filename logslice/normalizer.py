"""Field value normalization utilities for log records."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional


def normalize_field(
    record: Dict[str, Any],
    field: str,
    normalizer: Callable[[Any], Any],
) -> Dict[str, Any]:
    """Apply *normalizer* to *field* in *record*, returning a new record.

    If the field is absent the record is returned unchanged.
    """
    if field not in record:
        return dict(record)
    result = dict(record)
    result[field] = normalizer(record[field])
    return result


def normalize_fields(
    record: Dict[str, Any],
    field_normalizers: Dict[str, Callable[[Any], Any]],
) -> Dict[str, Any]:
    """Apply a mapping of field -> normalizer to *record*."""
    result = dict(record)
    for field, fn in field_normalizers.items():
        if field in result:
            result[field] = fn(result[field])
    return result


def strip_whitespace(value: Any) -> Any:
    """Strip leading/trailing whitespace from string values."""
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_bool(value: Any) -> Any:
    """Normalize common truthy/falsy strings to Python booleans."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in {"true", "yes", "1", "on"}:
            return True
        if value.lower() in {"false", "no", "0", "off"}:
            return False
    return value


def normalize_none(value: Any, none_strings: Optional[List[str]] = None) -> Any:
    """Convert empty / sentinel strings to ``None``."""
    sentinels = none_strings if none_strings is not None else ["", "null", "none", "nil", "-"]
    if isinstance(value, str) and value.lower() in {s.lower() for s in sentinels}:
        return None
    return value


def apply_normalizations(
    records: Iterable[Dict[str, Any]],
    field_normalizers: Dict[str, Callable[[Any], Any]],
) -> List[Dict[str, Any]]:
    """Apply *field_normalizers* to every record in *records*."""
    return [normalize_fields(r, field_normalizers) for r in records]

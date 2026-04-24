"""Field value formatting utilities for log records."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def format_field(
    record: Dict[str, Any],
    field: str,
    fmt: Callable[[Any], Any],
) -> Dict[str, Any]:
    """Return a new record with *field* transformed by *fmt*.

    If the field is absent the record is returned unchanged.
    """
    if field not in record:
        return dict(record)
    result = dict(record)
    result[field] = fmt(record[field])
    return result


def format_fields(
    record: Dict[str, Any],
    mapping: Dict[str, Callable[[Any], Any]],
) -> Dict[str, Any]:
    """Apply a mapping of {field: formatter} to *record*."""
    result = dict(record)
    for field, fmt in mapping.items():
        if field in result:
            result[field] = fmt(result[field])
    return result


def apply_formatters(
    records: List[Dict[str, Any]],
    mapping: Dict[str, Callable[[Any], Any]],
) -> List[Dict[str, Any]]:
    """Apply *mapping* formatters to every record in *records*."""
    return [format_fields(r, mapping) for r in records]


def uppercase_field(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Return record with *field* value uppercased (strings only)."""
    return format_field(
        record, field, lambda v: v.upper() if isinstance(v, str) else v
    )


def lowercase_field(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Return record with *field* value lowercased (strings only)."""
    return format_field(
        record, field, lambda v: v.lower() if isinstance(v, str) else v
    )


def cast_field(
    record: Dict[str, Any],
    field: str,
    typ: type,
    default: Optional[Any] = None,
) -> Dict[str, Any]:
    """Return record with *field* cast to *typ*, falling back to *default* on error."""
    def _cast(v: Any) -> Any:
        try:
            return typ(v)
        except (ValueError, TypeError):
            return default

    return format_field(record, field, _cast)


def rename_field(
    record: Dict[str, Any],
    old_name: str,
    new_name: str,
) -> Dict[str, Any]:
    """Return a new record with *old_name* key renamed to *new_name*.

    If *old_name* is absent the record is returned unchanged.  If *new_name*
    already exists it will be overwritten by the value from *old_name*.
    """
    if old_name not in record:
        return dict(record)
    result = dict(record)
    result[new_name] = result.pop(old_name)
    return result

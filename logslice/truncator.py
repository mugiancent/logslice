"""Truncate long string field values in log records."""

from typing import Any, Dict, List, Optional

DEFAULT_MAX_LENGTH = 100
DEFAULT_SUFFIX = "..."


def truncate_field(
    record: Dict[str, Any],
    field: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> Dict[str, Any]:
    """Return a copy of record with the named field truncated if it exceeds max_length."""
    if field not in record:
        return dict(record)
    value = record[field]
    if not isinstance(value, str) or len(value) <= max_length:
        return dict(record)
    result = dict(record)
    result[field] = value[:max_length] + suffix
    return result


def truncate_fields(
    record: Dict[str, Any],
    fields: List[str],
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> Dict[str, Any]:
    """Truncate multiple fields in a record."""
    result = dict(record)
    for field in fields:
        result = truncate_field(result, field, max_length, suffix)
    return result


def truncate_all_strings(
    record: Dict[str, Any],
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> Dict[str, Any]:
    """Truncate every string field in a record that exceeds max_length."""
    result = {}
    for key, value in record.items():
        if isinstance(value, str) and len(value) > max_length:
            result[key] = value[:max_length] + suffix
        else:
            result[key] = value
    return result


def apply_truncations(
    records: List[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> List[Dict[str, Any]]:
    """Apply truncation to a list of records.

    If fields is None, all string fields are truncated.
    """
    if fields is None:
        return [truncate_all_strings(r, max_length, suffix) for r in records]
    return [truncate_fields(r, fields, max_length, suffix) for r in records]

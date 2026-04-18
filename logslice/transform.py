"""Field transformation and projection utilities for log records."""
from typing import Any, Dict, List, Optional


def pick_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record containing only the specified fields."""
    return {k: record[k] for k in fields if k in record}


def drop_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record with the specified fields removed."""
    return {k: v for k, v in record.items() if k not in fields}


def rename_field(record: Dict[str, Any], old: str, new: str) -> Dict[str, Any]:
    """Return a new record with a field renamed."""
    if old not in record:
        return dict(record)
    result = dict(record)
    result[new] = result.pop(old)
    return result


def add_field(record: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Return a new record with an additional field."""
    result = dict(record)
    result[key] = value
    return result


def apply_transforms(
    record: Dict[str, Any],
    pick: Optional[List[str]] = None,
    drop: Optional[List[str]] = None,
    rename: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Apply a sequence of transformations to a record.

    Order: pick -> drop -> rename.
    """
    if pick:
        record = pick_fields(record, pick)
    if drop:
        record = drop_fields(record, drop)
    if rename:
        for old, new in rename.items():
            record = rename_field(record, old, new)
    return record

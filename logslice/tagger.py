"""Tag log records based on field values or patterns."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, Iterable, List, Optional

Record = Dict[str, Any]


def tag_by_field(
    record: Record,
    field: str,
    value: Any,
    tag: str,
    tag_field: str = "tags",
) -> Record:
    """Add *tag* to *tag_field* list when *field* equals *value*."""
    if record.get(field) != value:
        return record
    result = dict(record)
    existing: List[str] = list(result.get(tag_field) or [])
    if tag not in existing:
        existing.append(tag)
    result[tag_field] = existing
    return result


def tag_by_pattern(
    record: Record,
    field: str,
    pattern: str,
    tag: str,
    tag_field: str = "tags",
) -> Record:
    """Add *tag* when the string value of *field* matches *pattern*."""
    raw = record.get(field)
    if raw is None or not re.search(pattern, str(raw)):
        return record
    result = dict(record)
    existing: List[str] = list(result.get(tag_field) or [])
    if tag not in existing:
        existing.append(tag)
    result[tag_field] = existing
    return result


def tag_by_predicate(
    record: Record,
    predicate: Callable[[Record], bool],
    tag: str,
    tag_field: str = "tags",
) -> Record:
    """Add *tag* when *predicate(record)* is truthy."""
    if not predicate(record):
        return record
    result = dict(record)
    existing: List[str] = list(result.get(tag_field) or [])
    if tag not in existing:
        existing.append(tag)
    result[tag_field] = existing
    return result


def apply_tags(
    records: Iterable[Record],
    rules: List[Callable[[Record], Record]],
) -> List[Record]:
    """Apply a sequence of tagging rule callables to every record."""
    out: List[Record] = []
    for record in records:
        for rule in rules:
            record = rule(record)
        out.append(record)
    return out

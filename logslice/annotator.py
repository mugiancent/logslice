"""Annotate log records with computed metadata fields."""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, Iterable, List, Optional

Record = Dict[str, Any]


def annotate_with_index(
    records: Iterable[Record],
    field: str = "_index",
    start: int = 0,
) -> List[Record]:
    """Add a sequential index field to each record."""
    result = []
    for i, record in enumerate(records, start=start):
        annotated = dict(record)
        annotated[field] = i
        result.append(annotated)
    return result


def annotate_with_line_number(
    records: Iterable[Record],
    field: str = "_line",
    start: int = 1,
) -> List[Record]:
    """Add a 1-based line number field to each record."""
    return annotate_with_index(records, field=field, start=start)


def annotate_with_flag(
    records: Iterable[Record],
    predicate: Callable[[Record], bool],
    field: str = "_flagged",
    true_value: Any = True,
    false_value: Any = False,
) -> List[Record]:
    """Add a boolean flag field based on a predicate."""
    result = []
    for record in records:
        annotated = dict(record)
        annotated[field] = true_value if predicate(record) else false_value
        result.append(annotated)
    return result


def annotate_with_match(
    records: Iterable[Record],
    source_field: str,
    pattern: str,
    dest_field: str = "_match",
    no_match_value: Optional[str] = None,
) -> List[Record]:
    """Add a field with the first regex match found in source_field."""
    compiled = re.compile(pattern)
    result = []
    for record in records:
        annotated = dict(record)
        value = record.get(source_field, "")
        m = compiled.search(str(value))
        annotated[dest_field] = m.group(0) if m else no_match_value
        result.append(annotated)
    return result


def apply_annotations(
    records: Iterable[Record],
    annotations: List[Callable[[List[Record]], List[Record]]],
) -> List[Record]:
    """Apply a sequence of annotation functions to a list of records."""
    current = list(records)
    for fn in annotations:
        current = fn(current)
    return current

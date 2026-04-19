"""Deduplication of log records based on field subsets or full record equality."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, Tuple
import hashlib
import json


def _record_key(record: dict, fields: Optional[List[str]] = None) -> str:
    if fields:
        subset = {k: record.get(k) for k in fields}
    else:
        subset = record
    return hashlib.md5(json.dumps(subset, sort_keys=True, default=str).encode()).hexdigest()


def deduplicate(
    records: Iterable[dict],
    fields: Optional[List[str]] = None,
    keep: str = "first",
) -> Iterator[dict]:
    """Yield records with duplicates removed.

    Args:
        records: Iterable of parsed log records.
        fields: Fields to consider for equality. None means all fields.
        keep: 'first' keeps the first occurrence; 'last' keeps the final one.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    if keep == "first":
        seen: set = set()
        for record in records:
            key = _record_key(record, fields)
            if key not in seen:
                seen.add(key)
                yield record
    else:
        # keep == "last": buffer all, emit last seen per key
        latest: dict = {}
        order: List[str] = []
        for record in records:
            key = _record_key(record, fields)
            if key not in latest:
                order.append(key)
            latest[key] = record
        for key in order:
            yield latest[key]


def count_duplicates(
    records: Iterable[dict],
    fields: Optional[List[str]] = None,
) -> List[Tuple[dict, int]]:
    """Return each unique record paired with its occurrence count."""
    counts: dict = {}
    examples: dict = {}
    for record in records:
        key = _record_key(record, fields)
        counts[key] = counts.get(key, 0) + 1
        if key not in examples:
            examples[key] = record
    return [(examples[k], counts[k]) for k in examples]

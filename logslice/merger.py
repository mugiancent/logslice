"""Merge multiple sorted record streams into a single sorted sequence."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator


def _timestamp_key(record: dict) -> str:
    """Return a sortable timestamp string from a record, or empty string."""
    for field in ("timestamp", "time", "ts", "@timestamp"):
        val = record.get(field)
        if val is not None:
            return str(val)
    return ""


def merge_sorted(
    *streams: Iterable[dict],
    key: str | None = None,
) -> Iterator[dict]:
    """Merge pre-sorted record streams into one sorted stream.

    Each stream must already be sorted by the chosen key.  Uses a heap
    so memory usage is O(number of streams) rather than O(total records).

    Args:
        *streams: Any number of iterables of log record dicts.
        key: Field name to sort by.  When *None* the default timestamp
             heuristic is used.

    Yields:
        Records in merged sorted order.
    """
    def _key(record: dict) -> str:
        if key is not None:
            return str(record.get(key, ""))
        return _timestamp_key(record)

    iterators = [iter(s) for s in streams]
    heap: list[tuple[str, int, dict]] = []

    for idx, it in enumerate(iterators):
        try:
            record = next(it)
            heapq.heappush(heap, (_key(record), idx, record))
        except StopIteration:
            pass

    while heap:
        sort_val, idx, record = heapq.heappop(heap)
        yield record
        try:
            nxt = next(iterators[idx])
            heapq.heappush(heap, (_key(nxt), idx, nxt))
        except StopIteration:
            pass


def merge_unsorted(
    *streams: Iterable[dict],
    key: str | None = None,
) -> list[dict]:
    """Collect all records from all streams and sort them.

    Convenience wrapper for when the individual streams are not pre-sorted.
    """
    records = [r for stream in streams for r in stream]
    sort_field = key

    def _key(record: dict) -> str:
        if sort_field is not None:
            return str(record.get(sort_field, ""))
        return _timestamp_key(record)

    return sorted(records, key=_key)

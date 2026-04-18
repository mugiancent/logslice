"""Sorting utilities for log records."""

from typing import Any, Dict, Iterable, List, Optional
from logslice.filter import _extract_timestamp


def sort_records(
    records: Iterable[Dict[str, Any]],
    key: Optional[str] = None,
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Sort records by a field value or by timestamp if no key given.

    Args:
        records: Iterable of parsed log records.
        key: Field name to sort by. If None, sorts by timestamp.
        reverse: If True, sort in descending order.

    Returns:
        Sorted list of records. Records missing the sort key are placed last.
    """
    records_list = list(records)

    if key is None:
        def sort_key(record: Dict[str, Any]):
            ts = _extract_timestamp(record)
            return (ts is None, ts)
    else:
        def sort_key(record: Dict[str, Any]):
            val = record.get(key)
            return (val is None, val)

    return sorted(records_list, key=sort_key, reverse=reverse)


def deduplicate(
    records: Iterable[Dict[str, Any]],
    key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Remove duplicate records, optionally deduplicating by a single field.

    Args:
        records: Iterable of parsed log records.
        key: If provided, keep only the first record for each unique value of
             this field. If None, deduplicates on full record identity.

    Returns:
        De-duplicated list of records preserving original order.
    """
    seen = set()
    result: List[Dict[str, Any]] = []

    for record in records:
        if key is not None:
            marker = record.get(key)
        else:
            marker = tuple(sorted(record.items()))

        if marker not in seen:
            seen.add(marker)
            result.append(record)

    return result

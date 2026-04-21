"""Group and bucket log records by field values or time windows."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


def group_by_field(records: Iterable[dict], field: str) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records where *field* is absent are placed under the empty-string key.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        key = str(record.get(field, ""))
        buckets[key].append(record)
    return dict(buckets)


def group_by_time_window(
    records: Iterable[dict],
    window_seconds: int,
    timestamp_field: str = "timestamp",
) -> Dict[str, List[dict]]:
    """Bucket records into fixed-width time windows of *window_seconds*.

    The bucket key is an ISO-8601 string for the start of each window.
    Records whose timestamp cannot be parsed are placed under the empty-string key.
    """
    if window_seconds <= 0:
        raise ValueError("window_seconds must be a positive integer")

    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        raw = record.get(timestamp_field)
        key = _window_key(raw, window_seconds)
        buckets[key].append(record)
    return dict(buckets)


def _window_key(raw_timestamp: Optional[str], window_seconds: int) -> str:
    """Return the ISO-8601 window-start string for *raw_timestamp*."""
    if not raw_timestamp:
        return ""
    try:
        ts = datetime.fromisoformat(str(raw_timestamp).replace("Z", "+00:00"))
        epoch = ts.timestamp()
        window_start = int(epoch // window_seconds) * window_seconds
        dt = datetime.fromtimestamp(window_start, tz=timezone.utc)
        return dt.isoformat()
    except (ValueError, TypeError, OSError):
        return ""


def merge_groups(
    *group_maps: Dict[str, List[dict]],
) -> Dict[str, List[dict]]:
    """Merge multiple group-maps produced by the grouping helpers.

    Records for the same key are concatenated in order.
    """
    merged: Dict[str, List[dict]] = defaultdict(list)
    for gmap in group_maps:
        for key, records in gmap.items():
            merged[key].extend(records)
    return dict(merged)

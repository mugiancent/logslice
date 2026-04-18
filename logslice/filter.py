"""Filter log entries by time range or field value."""

from datetime import datetime
from typing import Any, Dict, List, Optional


TIMESTAMP_FIELDS = ("timestamp", "time", "ts", "@timestamp")


def _extract_timestamp(entry: Dict[str, Any]) -> Optional[datetime]:
    """Try to extract a datetime from common timestamp fields."""
    for field in TIMESTAMP_FIELDS:
        value = entry.get(field)
        if value is None:
            continue
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.utcfromtimestamp(value)
            except (OSError, OverflowError, ValueError):
                continue
        if isinstance(value, str):
            for fmt in (
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
            ):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
    return None


def filter_by_time(
    entries: List[Dict[str, Any]],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Return entries whose timestamp falls within [start, end]."""
    if start is None and end is None:
        return entries

    result = []
    for entry in entries:
        ts = _extract_timestamp(entry)
        if ts is None:
            continue
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        result.append(entry)
    return result


def filter_by_field(
    entries: List[Dict[str, Any]],
    field: str,
    value: Any,
) -> List[Dict[str, Any]]:
    """Return entries where entry[field] == value."""
    return [e for e in entries if e.get(field) == value]

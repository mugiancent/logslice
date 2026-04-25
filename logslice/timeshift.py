"""Shift or normalise timestamp fields across log records."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, Iterator

_DEFAULT_FIELD = "timestamp"


def _parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp string into a timezone-aware datetime."""
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Cannot parse timestamp: {value!r}")


def shift_record(
    record: dict,
    delta: timedelta,
    field: str = _DEFAULT_FIELD,
) -> dict:
    """Return a copy of *record* with *field* shifted by *delta*."""
    if field not in record:
        return dict(record)
    try:
        dt = _parse_ts(str(record[field]))
    except ValueError:
        return dict(record)
    shifted = dt + delta
    result = dict(record)
    result[field] = shifted.isoformat()
    return result


def shift_records(
    records: Iterable[dict],
    delta: timedelta,
    field: str = _DEFAULT_FIELD,
) -> Iterator[dict]:
    """Yield each record with its timestamp field shifted by *delta*."""
    for record in records:
        yield shift_record(record, delta, field=field)


def normalise_to_utc(
    record: dict,
    field: str = _DEFAULT_FIELD,
) -> dict:
    """Return a copy of *record* with *field* converted to UTC ISO-8601."""
    if field not in record:
        return dict(record)
    try:
        dt = _parse_ts(str(record[field]))
    except ValueError:
        return dict(record)
    result = dict(record)
    result[field] = dt.astimezone(timezone.utc).isoformat()
    return result


def rebase_records(
    records: Iterable[dict],
    new_start: datetime,
    field: str = _DEFAULT_FIELD,
) -> Iterator[dict]:
    """Shift all records so the earliest timestamp aligns with *new_start*."""
    items = list(records)
    timestamps = []
    for rec in items:
        try:
            timestamps.append(_parse_ts(str(rec[field])))
        except (KeyError, ValueError):
            pass
    if not timestamps:
        yield from items
        return
    if new_start.tzinfo is None:
        new_start = new_start.replace(tzinfo=timezone.utc)
    origin = min(timestamps)
    delta = new_start - origin
    yield from shift_records(items, delta, field=field)

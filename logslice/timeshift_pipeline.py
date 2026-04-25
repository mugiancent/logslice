"""Pipeline helpers that apply time-shifting operations to line streams."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Iterable, Iterator

from logslice.timeshift import normalise_to_utc, rebase_records, shift_records


def _parse_valid(lines: Iterable[str]) -> list[dict]:
    records: list[dict] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                records.append(obj)
        except json.JSONDecodeError:
            pass
    return records


def _emit(records: Iterable[dict]) -> str:
    return "\n".join(json.dumps(r) for r in records)


def shift_stream(
    lines: Iterable[str],
    seconds: float = 0,
    field: str = "timestamp",
) -> str:
    """Parse *lines* as JSONL, shift *field* by *seconds*, return JSONL string."""
    records = _parse_valid(lines)
    shifted = shift_records(records, timedelta(seconds=seconds), field=field)
    return _emit(shifted)


def normalise_stream(
    lines: Iterable[str],
    field: str = "timestamp",
) -> str:
    """Parse *lines* as JSONL, normalise *field* to UTC, return JSONL string."""
    records = _parse_valid(lines)
    normalised = (normalise_to_utc(r, field=field) for r in records)
    return _emit(normalised)


def rebase_stream(
    lines: Iterable[str],
    new_start: str,
    field: str = "timestamp",
) -> str:
    """Parse *lines* as JSONL, rebase timestamps to *new_start*, return JSONL.

    *new_start* must be an ISO-8601 string.  If it lacks timezone info UTC is
    assumed.
    """
    try:
        dt = datetime.fromisoformat(new_start)
    except ValueError as exc:
        raise ValueError(f"Invalid new_start timestamp: {new_start!r}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    records = _parse_valid(lines)
    rebased = rebase_records(records, dt, field=field)
    return _emit(rebased)

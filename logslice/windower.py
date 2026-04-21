"""windower.py – sliding and tumbling window operations over log records."""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, Iterator, List


def _ts(record: dict, field: str) -> float:
    """Return numeric timestamp from *field*, or 0.0 if absent/unparseable."""
    try:
        return float(record[field])
    except (KeyError, TypeError, ValueError):
        return 0.0


def tumbling_windows(
    records: Iterable[dict],
    width: float,
    ts_field: str = "timestamp",
) -> Iterator[tuple[float, List[dict]]]:
    """Yield (window_start, [records]) for non-overlapping windows of *width* seconds.

    Records are assumed to arrive in roughly chronological order.
    A window is emitted as soon as a record falls outside it.
    """
    if width <= 0:
        raise ValueError("width must be positive")

    window_start: float | None = None
    bucket: List[dict] = []

    for record in records:
        t = _ts(record, ts_field)
        if window_start is None:
            window_start = t

        if t < window_start + width:
            bucket.append(record)
        else:
            if bucket:
                yield window_start, bucket
            # advance window to the one that contains *t*
            steps = int((t - window_start) / width)
            window_start = window_start + steps * width
            bucket = [record]

    if bucket and window_start is not None:
        yield window_start, bucket


def sliding_windows(
    records: Iterable[dict],
    width: float,
    step: float,
    ts_field: str = "timestamp",
) -> Iterator[tuple[float, List[dict]]]:
    """Yield (window_start, [records]) for overlapping windows.

    *width*  – total span of each window in seconds.
    *step*   – how far each successive window is shifted.
    Both must be positive and *step* <= *width*.
    """
    if width <= 0 or step <= 0:
        raise ValueError("width and step must be positive")
    if step > width:
        raise ValueError("step must not exceed width")

    all_records = list(records)
    if not all_records:
        return

    first_ts = _ts(all_records[0], ts_field)
    last_ts = _ts(all_records[-1], ts_field)

    win_start = first_ts
    while win_start <= last_ts:
        win_end = win_start + width
        bucket = [
            r for r in all_records
            if win_start <= _ts(r, ts_field) < win_end
        ]
        yield win_start, bucket
        win_start += step


def window_counts(windows: Iterable[tuple[float, List[dict]]]) -> Dict[float, int]:
    """Reduce an iterable of (start, records) pairs to {start: count}."""
    return {start: len(recs) for start, recs in windows}

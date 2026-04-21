"""Pipeline helpers that integrate limiter operations with line-based I/O."""

from __future__ import annotations

from typing import Iterable

from logslice.limiter import take, skip, take_last, slice_records
from logslice.parser import parse_line
from logslice.output import format_record


def _parse_valid(lines: Iterable[str]) -> list[dict]:
    """Parse *lines*, silently dropping any that cannot be decoded."""
    records: list[dict] = []
    for line in lines:
        record = parse_line(line.rstrip("\n"))
        if record is not None:
            records.append(record)
    return records


def head(
    lines: Iterable[str],
    n: int,
    fmt: str = "json",
) -> list[str]:
    """Return formatted output for the first *n* valid records.

    Args:
        lines: Raw input lines (e.g. from a file or stdin).
        n: Maximum number of records to emit.
        fmt: Output format – ``"json"`` or ``"logfmt"``.

    Returns:
        A list of formatted record strings.
    """
    records = _parse_valid(lines)
    limited = take(records, n)
    return [format_record(r, fmt) for r in limited]


def tail(
    lines: Iterable[str],
    n: int,
    fmt: str = "json",
) -> list[str]:
    """Return formatted output for the last *n* valid records.

    Args:
        lines: Raw input lines.
        n: Number of trailing records to emit.
        fmt: Output format.

    Returns:
        A list of formatted record strings.
    """
    records = _parse_valid(lines)
    limited = take_last(records, n)
    return [format_record(r, fmt) for r in limited]


def window(
    lines: Iterable[str],
    start: int,
    stop: int,
    fmt: str = "json",
) -> list[str]:
    """Return formatted output for records at indices ``[start, stop)``.

    Args:
        lines: Raw input lines.
        start: Inclusive start index.
        stop: Exclusive stop index.
        fmt: Output format.

    Returns:
        A list of formatted record strings.
    """
    records = _parse_valid(lines)
    sliced = slice_records(records, start, stop)
    return [format_record(r, fmt) for r in sliced]

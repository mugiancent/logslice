"""High-level pipeline helpers that combine joining with parsing and formatting."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.joiner import inner_join, left_join
from logslice.parser import parse_line
from logslice.output import format_record

Record = Dict[str, Any]


def _parse_lines(lines: Iterable[str]) -> List[Record]:
    """Parse an iterable of raw log lines into records, skipping failures."""
    records: List[Record] = []
    for line in lines:
        record = parse_line(line.rstrip("\n"))
        if record is not None:
            records.append(record)
    return records


def join_streams(
    left_lines: Iterable[str],
    right_lines: Iterable[str],
    on: str,
    mode: str = "inner",
    right_prefix: str = "right_",
    fmt: str = "json",
) -> Iterator[str]:
    """Parse two line streams, join them, and yield formatted output lines.

    Parameters
    ----------
    left_lines:
        Raw log lines for the left side of the join.
    right_lines:
        Raw log lines for the right side of the join.
    on:
        Field name to join on.
    mode:
        ``'inner'`` (default) or ``'left'``.
    right_prefix:
        Prefix applied to field names taken from the right side.
    fmt:
        Output format – ``'json'`` or ``'logfmt'``.
    """
    left_records = _parse_lines(left_lines)
    right_records = _parse_lines(right_lines)

    if mode == "left":
        joined = left_join(left_records, right_records, on=on, right_prefix=right_prefix)
    else:
        joined = inner_join(left_records, right_records, on=on, right_prefix=right_prefix)

    for record in joined:
        yield format_record(record, fmt=fmt)

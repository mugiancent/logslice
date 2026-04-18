"""High-level pipeline combining parse, filter, transform, and output."""
from typing import Dict, Any, Iterable, Iterator, List, Optional

from logslice.parser import parse_line
from logslice.filter import filter_by_time, filter_by_field
from logslice.transform import apply_transforms
from logslice.output import format_record


def process_lines(
    lines: Iterable[str],
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    field_filters: Optional[List[str]] = None,
    pick: Optional[List[str]] = None,
    drop: Optional[List[str]] = None,
    rename: Optional[Dict[str, str]] = None,
    fmt: str = "json",
) -> Iterator[str]:
    """Parse, filter, transform and format an iterable of raw log lines.

    Yields formatted output lines ready for writing.
    """
    records: Iterable[Dict[str, Any]] = (
        r for raw in lines if (r := parse_line(raw.rstrip("\n"))) is not None
    )

    records = filter_by_time(records, start=start, end=end)

    if field_filters:
        for expr in field_filters:
            if "=" in expr:
                key, val = expr.split("=", 1)
                records = filter_by_field(records, key.strip(), val.strip())

    for record in records:
        transformed = apply_transforms(record, pick=pick, drop=drop, rename=rename)
        yield format_record(transformed, fmt=fmt)

"""End-to-end line processing pipeline."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.parser import parse_line
from logslice.filter import filter_by_time, filter_by_field
from logslice.transform import apply_transforms
from logslice.redactor import apply_redactions
from logslice.output import format_record


def process_lines(
    lines: Iterable[str],
    fmt: str = "json",
    start: Optional[str] = None,
    end: Optional[str] = None,
    field_filter: Optional[Dict[str, str]] = None,
    transforms: Optional[List[Dict[str, Any]]] = None,
    redact_fields: Optional[List[str]] = None,
    redact_patterns: Optional[List[str]] = None,
) -> Iterator[str]:
    """Parse, filter, transform, redact, and format each log line.

    Yields formatted output strings for every record that passes all filters.
    Lines that cannot be parsed are silently skipped.
    """
    records = (parse_line(line) for line in lines)
    valid = (r for r in records if r is not None)

    if start or end:
        valid = filter_by_time(valid, start=start, end=end)

    if field_filter:
        for key, value in field_filter.items():
            valid = filter_by_field(valid, key, value)

    if transforms:
        valid = (apply_transforms(r, transforms) for r in valid)

    if redact_fields or redact_patterns:
        valid = (
            apply_redactions(r, redact_field_list=redact_fields, redact_patterns=redact_patterns)
            for r in valid
        )

    for record in valid:
        yield format_record(record, fmt=fmt)


def count_lines(
    lines: Iterable[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
    field_filter: Optional[Dict[str, str]] = None,
) -> Dict[str, int]:
    """Count parsed, filtered, and skipped lines without producing output.

    Returns a dict with keys ``'total'``, ``'parsed'``, and ``'matched'``
    so callers can report basic pipeline statistics.
    """
    total = 0
    parsed = 0
    matched = 0

    for line in lines:
        total += 1
        record = parse_line(line)
        if record is None:
            continue
        parsed += 1
        # Reuse the filtering logic by delegating to process_lines with no
        # output formatting overhead beyond a simple sentinel format.
        records = [record]
        if start or end:
            from logslice.filter import filter_by_time  # noqa: F811
            records = list(filter_by_time(iter(records), start=start, end=end))
        if field_filter and records:
            from logslice.filter import filter_by_field  # noqa: F811
            for key, value in field_filter.items():
                records = list(filter_by_field(iter(records), key, value))
        matched += len(records)

    return {"total": total, "parsed": parsed, "matched": matched}

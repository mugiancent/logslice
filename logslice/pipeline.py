"""End-to-end pipeline: parse, filter, transform, sample, sort, output."""
from __future__ import annotations

from typing import Iterable, Iterator

from logslice.parser import parse_line
from logslice.filter import filter_by_time, filter_by_field
from logslice.transform import apply_transforms
from logslice.output import format_record
from logslice.sampler import sample_every_nth


def process_lines(
    lines: Iterable[str],
    *,
    start: str | None = None,
    end: str | None = None,
    field_filter: tuple[str, str] | None = None,
    transforms: list | None = None,
    fmt: str = "json",
    sample_n: int = 1,
) -> Iterator[str]:
    """Parse, filter, optionally transform and sample, then format each line."""
    records: list[dict] = []
    for line in lines:
        record = parse_line(line.rstrip("\n"))
        if record is None:
            continue
        records.append(record)

    records = list(filter_by_time(records, start=start, end=end))

    if field_filter is not None:
        key, value = field_filter
        records = list(filter_by_field(records, key, value))

    if transforms:
        records = [apply_transforms(r, transforms) for r in records]

    if sample_n > 1:
        records = list(sample_every_nth(records, sample_n))

    for record in records:
        yield format_record(record, fmt=fmt)

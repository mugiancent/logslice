"""Pipeline helpers that apply pivot/unpivot operations to line streams."""
import json
from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.parser import parse_line
from logslice.output import format_record
from logslice.pivot import pivot_records, unpivot_records, wide_to_long


def _parse_valid(lines: Iterable[str]) -> Iterator[Dict[str, Any]]:
    for line in lines:
        rec = parse_line(line.rstrip("\n"))
        if rec is not None:
            yield rec


def pivot_stream(
    lines: Iterable[str],
    index_field: str,
    column_field: str,
    value_field: str,
    fill_value: Any = None,
    fmt: str = "json",
) -> str:
    """Parse *lines*, pivot, and return formatted output."""
    records = list(_parse_valid(lines))
    pivoted = pivot_records(
        records,
        index_field=index_field,
        column_field=column_field,
        value_field=value_field,
        fill_value=fill_value,
    )
    return "\n".join(format_record(r, fmt) for r in pivoted)


def unpivot_stream(
    lines: Iterable[str],
    index_fields: List[str],
    column_field: str = "variable",
    value_field: str = "value",
    fmt: str = "json",
) -> str:
    """Parse *lines*, unpivot, and return formatted output."""
    records = _parse_valid(lines)
    melted = unpivot_records(
        records,
        index_fields=index_fields,
        column_field=column_field,
        value_field=value_field,
    )
    return "\n".join(format_record(r, fmt) for r in melted)


def wide_to_long_stream(
    lines: Iterable[str],
    id_field: str,
    value_fields: Optional[List[str]] = None,
    column_field: str = "metric",
    value_field: str = "value",
    fmt: str = "json",
) -> str:
    """Parse *lines*, convert wide to long, and return formatted output."""
    records = _parse_valid(lines)
    long_recs = wide_to_long(
        records,
        id_field=id_field,
        value_fields=value_fields,
        column_field=column_field,
        value_field=value_field,
    )
    return "\n".join(format_record(r, fmt) for r in long_recs)

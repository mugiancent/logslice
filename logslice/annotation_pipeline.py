"""High-level pipeline helpers for annotating log streams."""
from __future__ import annotations

import sys
from typing import Any, Dict, Iterable, List, Optional, TextIO

from logslice.annotator import (
    annotate_with_flag,
    annotate_with_index,
    annotate_with_match,
)
from logslice.parser import parse_line
from logslice.output import format_record

Record = Dict[str, Any]


def _parse_valid(lines: Iterable[str]) -> List[Record]:
    """Parse lines, silently dropping unparseable ones."""
    records: List[Record] = []
    for line in lines:
        record = parse_line(line.rstrip("\n"))
        if record is not None:
            records.append(record)
    return records


def annotate_stream(
    lines: Iterable[str],
    *,
    add_index: bool = False,
    index_field: str = "_index",
    flag_field: Optional[str] = None,
    flag_pattern: Optional[str] = None,
    flag_source: Optional[str] = None,
    match_field: Optional[str] = None,
    match_pattern: Optional[str] = None,
    match_source: Optional[str] = None,
    output_format: str = "json",
    out: TextIO = sys.stdout,
) -> int:
    """Parse *lines*, apply requested annotations, write formatted output.

    Returns the number of records written.
    """
    records = _parse_valid(lines)

    if add_index:
        records = annotate_with_index(records, field=index_field)

    if flag_field and flag_source and flag_pattern:
        import re
        compiled = re.compile(flag_pattern)
        records = annotate_with_flag(
            records,
            predicate=lambda r, _c=compiled, _s=flag_source: bool(
                _c.search(str(r.get(_s, "")))
            ),
            field=flag_field,
        )

    if match_field and match_source and match_pattern:
        records = annotate_with_match(
            records,
            source_field=match_source,
            pattern=match_pattern,
            dest_field=match_field,
        )

    for record in records:
        out.write(format_record(record, fmt=output_format) + "\n")

    return len(records)

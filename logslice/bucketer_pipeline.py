"""Pipeline helpers that apply bucketing to a stream of log lines."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

from logslice.bucketer import (
    bucket_by_range,
    bucket_by_value,
    bucket_counts,
    top_buckets,
)
from logslice.parser import parse_line

Record = Dict[str, Any]


def _parse_valid(lines: Iterable[str]) -> List[Record]:
    records: List[Record] = []
    for line in lines:
        record = parse_line(line.rstrip("\n"))
        if record is not None:
            records.append(record)
    return records


def value_bucket_summary(
    lines: Iterable[str],
    field: str,
    top: int = 0,
) -> str:
    """Parse *lines*, bucket by *field* value, and return a JSONL summary.

    Each output line is ``{"bucket": <label>, "count": <n>}``.
    If *top* > 0 only the *top* largest buckets are returned.
    """
    records = _parse_valid(lines)
    buckets = bucket_by_value(records, field)
    if top > 0:
        items = top_buckets(buckets, n=top)
    else:
        counts = bucket_counts(buckets)
        items = sorted(counts.items(), key=lambda x: x[0])
    rows = [{"bucket": k, "count": v} for k, v in items]
    return "\n".join(json.dumps(r) for r in rows)


def range_bucket_summary(
    lines: Iterable[str],
    field: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
    top: int = 0,
) -> str:
    """Parse *lines*, bin numeric *field* into ranges, return JSONL summary."""
    records = _parse_valid(lines)
    buckets = bucket_by_range(records, field, edges, labels=labels)
    if top > 0:
        items = top_buckets(buckets, n=top)
    else:
        counts = bucket_counts(buckets)
        items = sorted(counts.items(), key=lambda x: x[0])
    rows = [{"bucket": k, "count": v} for k, v in items]
    return "\n".join(json.dumps(r) for r in rows)

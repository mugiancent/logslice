"""Export records to various file formats (CSV, JSONL, TSV)."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable, List, Optional


def to_jsonl(records: Iterable[dict]) -> str:
    """Serialise records as newline-delimited JSON."""
    lines = [json.dumps(r, separators=(",", ":")) for r in records]
    return "\n".join(lines)


def to_csv(records: Iterable[dict], fields: Optional[List[str]] = None) -> str:
    """Serialise records as CSV.  Column order follows *fields* when given."""
    rows = list(records)
    if not rows:
        return ""
    if fields is None:
        fields = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def to_tsv(records: Iterable[dict], fields: Optional[List[str]] = None) -> str:
    """Serialise records as TSV."""
    rows = list(records)
    if not rows:
        return ""
    if fields is None:
        fields = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=fields, extrasaction="ignore",
        delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def export(records: Iterable[dict], fmt: str, fields: Optional[List[str]] = None) -> str:
    """Dispatch to the correct serialiser based on *fmt*."""
    rows = list(records)
    if fmt == "jsonl":
        return to_jsonl(rows)
    if fmt == "csv":
        return to_csv(rows, fields)
    if fmt == "tsv":
        return to_tsv(rows, fields)
    raise ValueError(f"Unknown export format: {fmt!r}")

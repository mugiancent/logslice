"""Import records from CSV or TSV files into dicts."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterator, List, Optional


def from_jsonl(text: str) -> Iterator[dict]:
    """Yield records from newline-delimited JSON text."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj
        except json.JSONDecodeError:
            pass


def from_csv(text: str, fields: Optional[List[str]] = None) -> Iterator[dict]:
    """Yield records from CSV text.  If *fields* given, use as header."""
    reader = csv.DictReader(io.StringIO(text), fieldnames=fields)
    for row in reader:
        yield dict(row)


def from_tsv(text: str, fields: Optional[List[str]] = None) -> Iterator[dict]:
    """Yield records from TSV text."""
    reader = csv.DictReader(io.StringIO(text), fieldnames=fields, delimiter="\t")
    for row in reader:
        yield dict(row)


def load(text: str, fmt: str, fields: Optional[List[str]] = None) -> Iterator[dict]:
    """Dispatch to the correct deserialiser based on *fmt*."""
    if fmt == "jsonl":
        return from_jsonl(text)
    if fmt == "csv":
        return from_csv(text, fields)
    if fmt == "tsv":
        return from_tsv(text, fields)
    raise ValueError(f"Unknown import format: {fmt!r}")

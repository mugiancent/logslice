"""Output formatting for logslice results."""
import json
import sys
from typing import Iterable


DEFAULT_FORMAT = "json"


def _to_logfmt(record: dict) -> str:
    parts = []
    for key, value in record.items():
        if value is None:
            value = ""
        value = str(value)
        if " " in value or "=" in value or '"' in value:
            value = '"' + value.replace('"', '\\"') + '"'
        parts.append(f"{key}={value}")
    return " ".join(parts)


def format_record(record: dict, fmt: str = DEFAULT_FORMAT) -> str:
    """Format a single log record as a string."""
    if fmt == "json":
        return json.dumps(record)
    elif fmt == "logfmt":
        return _to_logfmt(record)
    elif fmt == "pretty":
        lines = []
        for key, value in record.items():
            lines.append(f"  {key}: {value}")
        return "---\n" + "\n".join(lines)
    else:
        raise ValueError(f"Unknown output format: {fmt!r}")


def write_records(
    records: Iterable[dict],
    fmt: str = DEFAULT_FORMAT,
    output=None,
) -> int:
    """Write records to output stream. Returns count of records written."""
    if output is None:
        output = sys.stdout
    count = 0
    for record in records:
        output.write(format_record(record, fmt) + "\n")
        count += 1
    return count

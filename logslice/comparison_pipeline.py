"""Pipeline that compares two JSONL streams and emits a comparison report."""

from typing import Iterable, List, Optional

from logslice.importer import from_jsonl
from logslice.comparator import compare_records, summary
from logslice.exporter import to_jsonl


def _load(lines: Iterable[str]) -> List[dict]:
    """Parse JSONL lines into a list of records, skipping invalid lines."""
    return list(from_jsonl("\n".join(line.rstrip("\n") for line in lines)))


def compare_streams(
    left_lines: Iterable[str],
    right_lines: Iterable[str],
    key: str,
    only: Optional[str] = None,
) -> str:
    """Compare two JSONL streams keyed on *key* and return JSONL output.

    Parameters
    ----------
    left_lines:
        Iterable of raw text lines from the *left* (baseline) stream.
    right_lines:
        Iterable of raw text lines from the *right* (new) stream.
    key:
        Field name used to match records across streams.
    only:
        When given, restrict output to entries whose ``status`` equals *only*
        (e.g. ``"changed"``, ``"added"``, ``"removed"``).

    Returns
    -------
    str
        JSONL-formatted comparison entries.
    """
    left = _load(left_lines)
    right = _load(right_lines)
    comparisons = compare_records(left, right, key)
    if only:
        comparisons = [c for c in comparisons if c["status"] == only]
    return to_jsonl(comparisons)


def compare_summary(
    left_lines: Iterable[str],
    right_lines: Iterable[str],
    key: str,
) -> dict:
    """Return a summary dict of status counts for the two streams."""
    left = _load(left_lines)
    right = _load(right_lines)
    comparisons = compare_records(left, right, key)
    return summary(comparisons)

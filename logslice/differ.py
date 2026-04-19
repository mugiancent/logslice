"""Diff two sequences of log records and report added/removed/changed entries."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Tuple

Record = Dict[str, Any]


def diff_records(
    before: Iterable[Record],
    after: Iterable[Record],
    key: str,
) -> Iterator[Dict[str, Any]]:
    """Yield diff entries keyed by *key* field.

    Each entry has ``status`` of 'added', 'removed', or 'changed' and
    includes ``before`` / ``after`` snapshots where relevant.
    """
    before_map: Dict[str, Record] = {str(r[key]): r for r in before if key in r}
    after_map: Dict[str, Record] = {str(r[key]): r for r in after if key in r}

    all_keys = sorted(set(before_map) | set(after_map))
    for k in all_keys:
        if k not in before_map:
            yield {"status": "added", "key": k, "after": after_map[k]}
        elif k not in after_map:
            yield {"status": "removed", "key": k, "before": before_map[k]}
        elif before_map[k] != after_map[k]:
            yield {"status": "changed", "key": k, "before": before_map[k], "after": after_map[k]}


def changed_fields(before: Record, after: Record) -> List[Tuple[str, Any, Any]]:
    """Return list of (field, old_value, new_value) for differing fields."""
    all_fields = set(before) | set(after)
    diffs = []
    for f in sorted(all_fields):
        old = before.get(f)
        new = after.get(f)
        if old != new:
            diffs.append((f, old, new))
    return diffs


def summary(diffs: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    """Count diff entries by status."""
    counts: Dict[str, int] = {"added": 0, "removed": 0, "changed": 0}
    for d in diffs:
        status = d.get("status", "")
        if status in counts:
            counts[status] += 1
    return counts

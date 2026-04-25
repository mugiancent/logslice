"""Compare two sequences of log records and produce a structured diff report."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]


def _record_id(record: Record, key: str) -> Any:
    """Return the value used to match records across sequences."""
    return record.get(key)


def align_records(
    left: List[Record],
    right: List[Record],
    key: str,
) -> Iterator[Tuple[Optional[Record], Optional[Record]]]:
    """Pair records from *left* and *right* by *key*.

    Yields ``(left_record, right_record)`` tuples where either side may be
    ``None`` when a record exists only in one sequence.
    """
    left_index: Dict[Any, Record] = {_record_id(r, key): r for r in left}
    right_index: Dict[Any, Record] = {_record_id(r, key): r for r in right}
    all_keys = list(left_index) + [k for k in right_index if k not in left_index]
    for k in all_keys:
        yield left_index.get(k), right_index.get(k)


def compare_records(
    left: List[Record],
    right: List[Record],
    key: str,
) -> List[Dict[str, Any]]:
    """Return a list of comparison entries for every aligned record pair.

    Each entry has:
    - ``status``: ``"added"``, ``"removed"``, ``"changed"``, or ``"equal"``
    - ``key_value``: the value of *key* for this pair
    - ``changes``: list of ``{field, left, right}`` dicts (only when changed)
    """
    results: List[Dict[str, Any]] = []
    for lrec, rrec in align_records(left, right, key):
        if lrec is None:
            results.append({"status": "added", "key_value": _record_id(rrec, key), "changes": []})
        elif rrec is None:
            results.append({"status": "removed", "key_value": _record_id(lrec, key), "changes": []})
        else:
            all_fields = set(lrec) | set(rrec)
            changes = [
                {"field": f, "left": lrec.get(f), "right": rrec.get(f)}
                for f in sorted(all_fields)
                if lrec.get(f) != rrec.get(f)
            ]
            status = "changed" if changes else "equal"
            results.append({"status": status, "key_value": _record_id(lrec, key), "changes": changes})
    return results


def summary(comparisons: List[Dict[str, Any]]) -> Dict[str, int]:
    """Return counts of each status across *comparisons*."""
    counts: Dict[str, int] = {"added": 0, "removed": 0, "changed": 0, "equal": 0}
    for entry in comparisons:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return counts

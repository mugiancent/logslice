"""Line and field counting utilities for logslice."""
from typing import Iterable, Dict, Any, List
from collections import Counter


def count_records(records: Iterable[Dict[str, Any]]) -> int:
    """Return total number of records."""
    return sum(1 for _ in records)


def count_field_values(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count occurrences of each distinct value for *field*."""
    counter: Counter = Counter()
    for record in records:
        if field in record:
            counter[str(record[field])] += 1
    return dict(counter)


def count_fields_present(records: Iterable[Dict[str, Any]], fields: List[str]) -> Dict[str, int]:
    """For each field name, count how many records contain it."""
    totals: Dict[str, int] = {f: 0 for f in fields}
    for record in records:
        for f in fields:
            if f in record:
                totals[f] += 1
    return totals


def top_n(counts: Dict[str, int], n: int = 10) -> List[tuple]:
    """Return the top-n (value, count) pairs sorted by count descending."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

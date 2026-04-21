"""Score log records based on field presence, value matches, and pattern hits."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Tuple

Record = Dict[str, Any]
Rule = Tuple[Callable[[Record], bool], float]


def make_field_presence_rule(field: str, weight: float = 1.0) -> Rule:
    """Award *weight* points when *field* exists in the record."""
    return (lambda r: field in r, weight)


def make_field_value_rule(field: str, value: Any, weight: float = 1.0) -> Rule:
    """Award *weight* points when *field* equals *value*."""
    return (lambda r: r.get(field) == value, weight)


def make_pattern_rule(field: str, pattern: str, weight: float = 1.0) -> Rule:
    """Award *weight* points when *field* value matches *pattern* (regex)."""
    compiled = re.compile(pattern)

    def _pred(r: Record) -> bool:
        val = r.get(field)
        return bool(compiled.search(str(val))) if val is not None else False

    return (_pred, weight)


def score_record(record: Record, rules: List[Rule]) -> float:
    """Return the sum of weights for every rule that matches *record*."""
    return sum(weight for pred, weight in rules if pred(record))


def score_records(
    records: List[Record],
    rules: List[Rule],
    *,
    min_score: float = 0.0,
) -> List[Tuple[float, Record]]:
    """Score every record and return ``(score, record)`` pairs.

    Only pairs whose score is >= *min_score* are included.
    Results are sorted by score descending.
    """
    scored = [
        (score_record(r, rules), r)
        for r in records
    ]
    return sorted(
        [(s, r) for s, r in scored if s >= min_score],
        key=lambda t: t[0],
        reverse=True,
    )


def top_scored(
    records: List[Record],
    rules: List[Rule],
    n: int,
    *,
    min_score: float = 0.0,
) -> List[Record]:
    """Return the top *n* records by score."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return [r for _, r in score_records(records, rules, min_score=min_score)[:n]]

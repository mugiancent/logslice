"""High-level pipeline helpers that combine parsing, scoring, and output."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from logslice.parser import parse_line
from logslice.scorer import (
    Rule,
    make_field_presence_rule,
    make_field_value_rule,
    make_pattern_rule,
    score_records,
    top_scored,
)
from logslice.output import format_record

Record = Dict[str, Any]


def _parse_valid(lines: Iterable[str]) -> List[Record]:
    records = []
    for line in lines:
        rec = parse_line(line.rstrip("\n"))
        if rec is not None:
            records.append(rec)
    return records


def build_rules(
    presence: Optional[List[str]] = None,
    values: Optional[List[Tuple[str, Any, float]]] = None,
    patterns: Optional[List[Tuple[str, str, float]]] = None,
    presence_weight: float = 1.0,
) -> List[Rule]:
    """Construct a list of scoring rules from declarative config.

    Parameters
    ----------
    presence:
        Field names that should earn *presence_weight* each when present.
    values:
        Sequence of ``(field, value, weight)`` tuples.
    patterns:
        Sequence of ``(field, regex_pattern, weight)`` tuples.
    presence_weight:
        Default weight applied to presence rules.
    """
    rules: List[Rule] = []
    for field in (presence or []):
        rules.append(make_field_presence_rule(field, presence_weight))
    for field, value, weight in (values or []):
        rules.append(make_field_value_rule(field, value, weight))
    for field, pattern, weight in (patterns or []):
        rules.append(make_pattern_rule(field, pattern, weight))
    return rules


def rank_lines(
    lines: Iterable[str],
    rules: List[Rule],
    *,
    min_score: float = 0.0,
    fmt: str = "json",
) -> List[str]:
    """Parse *lines*, score every record, and return formatted output lines.

    Records are ordered by score descending.  Lines that cannot be parsed
    are silently skipped.
    """
    records = _parse_valid(lines)
    scored = score_records(records, rules, min_score=min_score)
    return [format_record(rec, fmt) for _, rec in scored]


def top_lines(
    lines: Iterable[str],
    rules: List[Rule],
    n: int,
    *,
    min_score: float = 0.0,
    fmt: str = "json",
) -> List[str]:
    """Return the top *n* formatted lines by score."""
    records = _parse_valid(lines)
    top = top_scored(records, rules, n, min_score=min_score)
    return [format_record(rec, fmt) for rec in top]

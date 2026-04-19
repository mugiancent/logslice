"""Profile structured log records to infer field types and coverage."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List


def _infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "null"


def profile_fields(records: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Return per-field stats: count, coverage, and observed types."""
    total = 0
    counts: Dict[str, int] = defaultdict(int)
    types: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for record in records:
        total += 1
        for key, value in record.items():
            counts[key] += 1
            types[key][_infer_type(value)] += 1

    result: Dict[str, Dict[str, Any]] = {}
    for field in counts:
        result[field] = {
            "count": counts[field],
            "coverage": counts[field] / total if total else 0.0,
            "types": dict(types[field]),
        }
    return result


def field_names(records: Iterable[Dict[str, Any]]) -> List[str]:
    """Return sorted list of all field names seen across records."""
    seen: set = set()
    for record in records:
        seen.update(record.keys())
    return sorted(seen)


def coverage_report(profile: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return rows sorted by coverage descending for display."""
    rows = [
        {"field": f, "coverage": v["coverage"], "count": v["count"], "types": v["types"]}
        for f, v in profile.items()
    ]
    rows.sort(key=lambda r: r["coverage"], reverse=True)
    return rows

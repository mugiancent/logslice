"""Clamp numeric field values to a specified [min, max] range."""

from typing import Any, Dict, List, Optional, Union

Number = Union[int, float]
Record = Dict[str, Any]


def clamp_value(value: Any, lo: Optional[Number], hi: Optional[Number]) -> Any:
    """Return *value* clamped to [lo, hi].  Non-numeric values are returned unchanged."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return value
    if lo is not None:
        value = max(lo, value)
    if hi is not None:
        value = min(hi, value)
    return value


def clamp_field(
    record: Record,
    field: str,
    lo: Optional[Number] = None,
    hi: Optional[Number] = None,
) -> Record:
    """Return a new record with *field* clamped to [lo, hi].

    Missing fields and non-numeric values are left unchanged.
    """
    if field not in record:
        return record
    return {**record, field: clamp_value(record[field], lo, hi)}


def clamp_fields(
    record: Record,
    clamps: Dict[str, Dict[str, Optional[Number]]],
) -> Record:
    """Apply multiple clamp operations defined by *clamps*.

    *clamps* maps field name -> {"lo": ..., "hi": ...}.
    """
    result = record
    for field, bounds in clamps.items():
        lo = bounds.get("lo")
        hi = bounds.get("hi")
        result = clamp_field(result, field, lo, hi)
    return result


def clamp_all_numeric(
    record: Record,
    lo: Optional[Number] = None,
    hi: Optional[Number] = None,
) -> Record:
    """Clamp every numeric field in *record* to [lo, hi]."""
    return {
        k: clamp_value(v, lo, hi) for k, v in record.items()
    }


def apply_clamps(
    records: List[Record],
    clamps: Dict[str, Dict[str, Optional[Number]]],
) -> List[Record]:
    """Apply *clamps* to every record in *records* and return a new list."""
    return [clamp_fields(r, clamps) for r in records]

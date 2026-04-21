"""Type coercion utilities for log record fields."""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional


def coerce_field(
    record: Dict[str, Any],
    field: str,
    coerce_fn: Callable[[Any], Any],
    default: Optional[Any] = None,
) -> Dict[str, Any]:
    """Return a new record with *field* coerced via *coerce_fn*.

    If the field is missing the record is returned unchanged.
    If coercion raises, *default* is used (None means leave original value).
    """
    if field not in record:
        return record
    result = dict(record)
    try:
        result[field] = coerce_fn(record[field])
    except (ValueError, TypeError):
        if default is not None:
            result[field] = default
        # else leave original value untouched
    return result


def coerce_to_int(record: Dict[str, Any], field: str, default: Optional[int] = None) -> Dict[str, Any]:
    """Coerce *field* to int."""
    return coerce_field(record, field, int, default)


def coerce_to_float(record: Dict[str, Any], field: str, default: Optional[float] = None) -> Dict[str, Any]:
    """Coerce *field* to float."""
    return coerce_field(record, field, float, default)


def coerce_to_str(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Coerce *field* to str."""
    return coerce_field(record, field, str)


def coerce_to_bool(record: Dict[str, Any], field: str, default: Optional[bool] = None) -> Dict[str, Any]:
    """Coerce *field* to bool.

    String values 'true'/'1'/'yes' (case-insensitive) -> True;
    'false'/'0'/'no' -> False.
    """
    def _to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
        raise ValueError(f"Cannot coerce {value!r} to bool")

    return coerce_field(record, field, _to_bool, default)


def apply_coercions(
    records: Iterable[Dict[str, Any]],
    coercions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply a list of coercion specs to every record.

    Each spec is a dict with keys:
      - ``field``  (str)  – field name to coerce
      - ``type``   (str)  – one of 'int', 'float', 'str', 'bool'
      - ``default``       – optional fallback value on coercion failure
    """
    _dispatch: Dict[str, Callable[..., Dict[str, Any]]] = {
        "int": coerce_to_int,
        "float": coerce_to_float,
        "str": coerce_to_str,
        "bool": coerce_to_bool,
    }
    results: List[Dict[str, Any]] = []
    for record in records:
        for spec in coercions:
            field = spec["field"]
            type_name = spec.get("type", "str")
            default = spec.get("default")
            fn = _dispatch.get(type_name)
            if fn is None:
                continue
            if type_name == "str":
                record = coerce_to_str(record, field)
            else:
                record = fn(record, field, default)
        results.append(record)
    return results

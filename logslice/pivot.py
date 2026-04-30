"""Pivot and unpivot records for reshaping structured log data."""
from typing import Any, Dict, Iterable, Iterator, List, Optional


def pivot_records(
    records: Iterable[Dict[str, Any]],
    index_field: str,
    column_field: str,
    value_field: str,
    fill_value: Any = None,
) -> List[Dict[str, Any]]:
    """Pivot records so unique values of *column_field* become new keys.

    Each distinct value of *index_field* produces one output record whose
    extra keys are the distinct values of *column_field*, mapped to the
    corresponding *value_field*.
    """
    rows: Dict[Any, Dict[str, Any]] = {}
    columns: List[Any] = []
    seen_columns: set = set()

    for rec in records:
        idx = rec.get(index_field)
        col = rec.get(column_field)
        val = rec.get(value_field, fill_value)

        if idx not in rows:
            rows[idx] = {index_field: idx}

        if col not in seen_columns:
            seen_columns.add(col)
            columns.append(col)

        rows[idx][col] = val

    # Fill missing combinations with fill_value
    for row in rows.values():
        for col in columns:
            if col not in row:
                row[col] = fill_value

    return list(rows.values())


def unpivot_records(
    records: Iterable[Dict[str, Any]],
    index_fields: List[str],
    column_field: str = "variable",
    value_field: str = "value",
) -> Iterator[Dict[str, Any]]:
    """Unpivot (melt) records: turn non-index columns into rows.

    Each non-index key in a record becomes a separate output record with
    *column_field* set to the original key and *value_field* set to its value.
    """
    index_set = set(index_fields)
    for rec in records:
        base = {k: v for k, v in rec.items() if k in index_set}
        for key, val in rec.items():
            if key not in index_set:
                yield {**base, column_field: key, value_field: val}


def wide_to_long(
    records: Iterable[Dict[str, Any]],
    id_field: str,
    value_fields: Optional[List[str]] = None,
    column_field: str = "metric",
    value_field: str = "value",
) -> Iterator[Dict[str, Any]]:
    """Convert wide-format records to long format for a subset of fields."""
    for rec in records:
        keys = value_fields if value_fields is not None else [
            k for k in rec if k != id_field
        ]
        for key in keys:
            if key in rec:
                yield {id_field: rec.get(id_field), column_field: key, value_field: rec[key]}

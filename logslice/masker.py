"""masker.py – partially mask field values for privacy (e.g. show only last 4 chars)."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

Record = Dict[str, Any]

_DEFAULT_MASK = "*"


def mask_field(
    record: Record,
    field: str,
    *,
    keep_start: int = 0,
    keep_end: int = 0,
    mask_char: str = _DEFAULT_MASK,
) -> Record:
    """Return a copy of *record* with *field* partially masked.

    Characters outside the *keep_start* / *keep_end* windows are replaced with
    *mask_char*.  If the value is not a string it is left unchanged.
    """
    if field not in record:
        return dict(record)
    value = record[field]
    if not isinstance(value, str):
        return dict(record)
    n = len(value)
    visible = keep_start + keep_end
    if visible >= n:
        return dict(record)
    masked_len = n - visible
    masked = (
        value[:keep_start]
        + mask_char * masked_len
        + (value[n - keep_end:] if keep_end else "")
    )
    return {**record, field: masked}


def mask_pattern(
    record: Record,
    field: str,
    pattern: str,
    replacement: str = _DEFAULT_MASK * 4,
) -> Record:
    """Replace regex *pattern* matches inside *field* with *replacement*."""
    if field not in record:
        return dict(record)
    value = record[field]
    if not isinstance(value, str):
        return dict(record)
    return {**record, field: re.sub(pattern, replacement, value)}


def apply_masks(
    records: Iterable[Record],
    field_specs: Optional[List[Dict[str, Any]]] = None,
    pattern_specs: Optional[List[Dict[str, Any]]] = None,
) -> List[Record]:
    """Apply a sequence of masking operations to every record.

    *field_specs* is a list of dicts accepted by :func:`mask_field`.
    *pattern_specs* is a list of dicts accepted by :func:`mask_pattern`.
    """
    field_specs = field_specs or []
    pattern_specs = pattern_specs or []
    result: List[Record] = []
    for record in records:
        r = record
        for spec in field_specs:
            r = mask_field(r, **spec)
        for spec in pattern_specs:
            r = mask_pattern(r, **spec)
        result.append(r)
    return result

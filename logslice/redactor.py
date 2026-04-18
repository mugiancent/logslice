"""Field value redaction for sensitive log data."""

import re
from typing import Any, Dict, List, Optional


DEFAULT_MASK = "***"


def redact_fields(record: Dict[str, Any], fields: List[str], mask: str = DEFAULT_MASK) -> Dict[str, Any]:
    """Replace values of specified fields with a mask string."""
    result = dict(record)
    for field in fields:
        if field in result:
            result[field] = mask
    return result


def redact_pattern(
    record: Dict[str, Any],
    pattern: str,
    mask: str = DEFAULT_MASK,
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Replace substrings matching a regex pattern in string field values.

    If *fields* is given, only those fields are scanned; otherwise all fields.
    """
    compiled = re.compile(pattern)
    result = dict(record)
    targets = fields if fields is not None else list(result.keys())
    for key in targets:
        value = result.get(key)
        if isinstance(value, str):
            result[key] = compiled.sub(mask, value)
    return result


def apply_redactions(
    record: Dict[str, Any],
    redact_field_list: Optional[List[str]] = None,
    redact_patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> Dict[str, Any]:
    """Apply all configured redactions to a single record."""
    if redact_field_list:
        record = redact_fields(record, redact_field_list, mask=mask)
    if redact_patterns:
        for pat in redact_patterns:
            record = redact_pattern(record, pat, mask=mask)
    return record

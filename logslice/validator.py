"""Field validation for log records."""
from typing import Any, Callable, Dict, List, Optional


ValidationError = Dict[str, str]


def require_fields(record: Dict[str, Any], fields: List[str]) -> List[ValidationError]:
    """Return errors for any required fields missing from record."""
    errors = []
    for field in fields:
        if field not in record:
            errors.append({"field": field, "error": "missing required field"})
    return errors


def require_type(record: Dict[str, Any], field: str, expected_type: type) -> List[ValidationError]:
    """Return an error if field exists but is not of expected_type."""
    if field not in record:
        return []
    if not isinstance(record[field], expected_type):
        return [
            {
                "field": field,
                "error": f"expected {expected_type.__name__}, got {type(record[field]).__name__}",
            }
        ]
    return []


def require_pattern(record: Dict[str, Any], field: str, pattern: str) -> List[ValidationError]:
    """Return an error if field value does not match regex pattern."""
    import re
    if field not in record:
        return []
    value = str(record[field])
    if not re.fullmatch(pattern, value):
        return [{"field": field, "error": f"value {value!r} does not match pattern {pattern!r}"}]
    return []


def apply_validations(
    record: Dict[str, Any],
    rules: List[Callable[[Dict[str, Any]], List[ValidationError]]],
) -> List[ValidationError]:
    """Run all validation rules against a record and collect errors."""
    errors: List[ValidationError] = []
    for rule in rules:
        errors.extend(rule(record))
    return errors


def is_valid(
    record: Dict[str, Any],
    rules: List[Callable[[Dict[str, Any]], List[ValidationError]]],
) -> bool:
    """Return True if record passes all validation rules."""
    return len(apply_validations(record, rules)) == 0

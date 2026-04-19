"""Pipeline helpers that combine schema validation with record streaming."""
from typing import Dict, Any, Iterable, Iterator, List, Tuple

from logslice.schema import Schema


def validate_records(
    records: Iterable[Dict[str, Any]],
    schema: Schema,
) -> Iterator[Dict[str, Any]]:
    """Yield only records that pass schema validation."""
    for record in records:
        if schema.is_valid(record):
            yield record


def validate_records_with_errors(
    records: Iterable[Dict[str, Any]],
    schema: Schema,
) -> Iterator[Tuple[Dict[str, Any], List[str]]]:
    """Yield (record, errors) tuples for every record; errors is empty on success."""
    for record in records:
        errors = schema.validate(record)
        yield record, errors


def partition_records(
    records: Iterable[Dict[str, Any]],
    schema: Schema,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Split records into (valid, invalid) lists."""
    valid: List[Dict[str, Any]] = []
    invalid: List[Dict[str, Any]] = []
    for record in records:
        (valid if schema.is_valid(record) else invalid).append(record)
    return valid, invalid

"""Integration of schema validation into the log processing pipeline."""
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple
from logslice.schema import Schema
from logslice.validator import ValidationError


def validate_records(
    records: Iterable[Dict[str, Any]],
    schema: Schema,
    drop_invalid: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Yield records that pass schema validation, optionally dropping failures."""
    for record in records:
        if schema.is_valid(record):
            yield record
        elif not drop_invalid:
            yield record


def validate_records_with_errors(
    records: Iterable[Dict[str, Any]],
    schema: Schema,
) -> Iterator[Tuple[Dict[str, Any], List[ValidationError]]]:
    """Yield (record, errors) tuples for every record."""
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

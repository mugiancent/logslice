"""Validate records through a Schema, partitioning valid from invalid."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, List, Tuple

from logslice.schema import Schema

Record = Dict[str, Any]


def validate_records(records: Iterable[Record], schema: Schema) -> Iterator[Record]:
    """Yield only records that pass *schema* validation."""
    for record in records:
        if schema.is_valid(record):
            yield record


def validate_records_with_errors(
    records: Iterable[Record], schema: Schema
) -> Iterator[Tuple[Record, List[str]]]:
    """Yield (record, errors) tuples; errors is empty list when valid."""
    for record in records:
        errors = schema.validate(record)
        yield record, errors


def partition_records(
    records: Iterable[Record], schema: Schema
) -> Tuple[List[Record], List[Tuple[Record, List[str]]]]:
    """Split records into (valid, invalid) where invalid carries error lists."""
    valid: List[Record] = []
    invalid: List[Tuple[Record, List[str]]] = []
    for record, errors in validate_records_with_errors(records, schema):
        if errors:
            invalid.append((record, errors))
        else:
            valid.append(record)
    return valid, invalid

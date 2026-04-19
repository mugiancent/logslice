"""Field enrichment: derive or inject new fields into log records."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, Iterable, List

Record = Dict[str, Any]
Enricher = Callable[[Record], Record]


def add_derived_field(dest: str, source: str, fn: Callable[[Any], Any]) -> Enricher:
    """Return an enricher that sets *dest* to fn(record[source]).

    If *source* is missing the record is returned unchanged.
    """
    def _enrich(record: Record) -> Record:
        if source not in record:
            return record
        result = dict(record)
        result[dest] = fn(record[source])
        return result
    return _enrich


def add_static_field(key: str, value: Any) -> Enricher:
    """Return an enricher that unconditionally sets *key* to *value*."""
    def _enrich(record: Record) -> Record:
        result = dict(record)
        result[key] = value
        return result
    return _enrich


def add_regex_capture(dest: str, source: str, pattern: str, group: int | str = 1) -> Enricher:
    """Extract a regex group from *source* and store it in *dest*.

    If the pattern does not match the record is returned unchanged.
    """
    compiled = re.compile(pattern)

    def _enrich(record: Record) -> Record:
        value = record.get(source)
        if not isinstance(value, str):
            return record
        m = compiled.search(value)
        if not m:
            return record
        result = dict(record)
        result[dest] = m.group(group)
        return result
    return _enrich


def apply_enrichments(records: Iterable[Record], enrichers: List[Enricher]) -> Iterable[Record]:
    """Apply a sequence of enrichers to every record."""
    for record in records:
        for enricher in enrichers:
            record = enricher(record)
        yield record

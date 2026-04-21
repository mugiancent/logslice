"""High-level tagging pipeline helpers."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from logslice.tagger import (
    apply_tags,
    tag_by_field,
    tag_by_pattern,
    tag_by_predicate,
)

Record = Dict[str, Any]
RuleSpec = Dict[str, Any]


def build_rules(specs: List[RuleSpec], tag_field: str = "tags") -> List[Callable[[Record], Record]]:
    """Build a list of tagging callables from declarative spec dicts.

    Each spec must contain a ``tag`` key and exactly one of:
    - ``field`` + ``value``  -> tag_by_field
    - ``field`` + ``pattern`` -> tag_by_pattern
    - ``predicate``           -> tag_by_predicate (a callable)
    """
    rules: List[Callable[[Record], Record]] = []
    for spec in specs:
        tag = spec["tag"]
        if "predicate" in spec:
            pred = spec["predicate"]
            rules.append(
                lambda r, p=pred, t=tag, tf=tag_field: tag_by_predicate(r, p, t, tf)
            )
        elif "pattern" in spec:
            field = spec["field"]
            pattern = spec["pattern"]
            rules.append(
                lambda r, f=field, pat=pattern, t=tag, tf=tag_field: tag_by_pattern(
                    r, f, pat, t, tf
                )
            )
        elif "value" in spec:
            field = spec["field"]
            value = spec["value"]
            rules.append(
                lambda r, f=field, v=value, t=tag, tf=tag_field: tag_by_field(
                    r, f, v, t, tf
                )
            )
        else:
            raise ValueError(f"Invalid rule spec (no value/pattern/predicate): {spec}")
    return rules


def tag_records(
    records: Iterable[Record],
    specs: List[RuleSpec],
    tag_field: str = "tags",
) -> List[Record]:
    """Convenience function: build rules from *specs* and apply to *records*."""
    rules = build_rules(specs, tag_field=tag_field)
    return apply_tags(records, rules)


def partition_by_tag(
    records: Iterable[Record],
    tag: str,
    tag_field: str = "tags",
) -> Tuple[List[Record], List[Record]]:
    """Split records into (tagged, untagged) based on presence of *tag*."""
    tagged: List[Record] = []
    untagged: List[Record] = []
    for record in records:
        tags = record.get(tag_field) or []
        (tagged if tag in tags else untagged).append(record)
    return tagged, untagged

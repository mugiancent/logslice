"""Route log records to different outputs based on field predicates."""
from typing import Any, Callable, Dict, Iterable, List, Tuple

Record = Dict[str, Any]
Predicate = Callable[[Record], bool]
Route = Tuple[str, Predicate]


def make_predicate(field: str, value: Any) -> Predicate:
    """Return a predicate that matches records where field == value."""
    def _pred(record: Record) -> bool:
        return record.get(field) == value
    return _pred


def make_regex_predicate(field: str, pattern: str) -> Predicate:
    """Return a predicate that matches records where field matches pattern."""
    import re
    compiled = re.compile(pattern)
    def _pred(record: Record) -> bool:
        val = record.get(field, "")
        return bool(compiled.search(str(val)))
    return _pred


def route_records(
    records: Iterable[Record],
    routes: List[Route],
    default: str = "default",
) -> Dict[str, List[Record]]:
    """Distribute records into named buckets based on ordered route predicates.

    The first matching route wins. Unmatched records go to *default*.
    """
    buckets: Dict[str, List[Record]] = {default: []}
    for name, _ in routes:
        buckets.setdefault(name, [])

    for record in records:
        matched = False
        for name, predicate in routes:
            if predicate(record):
                buckets[name].append(record)
                matched = True
                break
        if not matched:
            buckets[default].append(record)

    return buckets


def route_to_files(
    records: Iterable[Record],
    routes: List[Route],
    default: str = "default",
) -> Dict[str, List[Record]]:
    """Alias for route_records kept for semantic clarity."""
    return route_records(records, routes, default=default)

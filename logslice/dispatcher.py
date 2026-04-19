"""Dispatch routed record buckets to writers or collectors."""
from typing import Any, Callable, Dict, Iterable, List

Record = Dict[str, Any]
Writer = Callable[[Iterable[Record]], None]


def dispatch(
    buckets: Dict[str, List[Record]],
    writers: Dict[str, Writer],
    default_writer: Writer | None = None,
) -> Dict[str, int]:
    """Call each writer with its bucket of records.

    Returns a dict mapping bucket name -> number of records dispatched.
    Buckets without a matching writer use *default_writer* if provided.
    """
    counts: Dict[str, int] = {}
    for name, records in buckets.items():
        writer = writers.get(name, default_writer)
        if writer is not None:
            writer(records)
        counts[name] = len(records)
    return counts


def collect_buckets(
    buckets: Dict[str, List[Record]],
) -> Dict[str, List[Record]]:
    """Return a shallow copy of the buckets dict (utility for testing/piping)."""
    return {name: list(records) for name, records in buckets.items()}


def fanout(
    records: Iterable[Record],
    writers: List[Writer],
) -> int:
    """Send every record to every writer. Returns total records processed."""
    records = list(records)
    for writer in writers:
        writer(records)
    return len(records)

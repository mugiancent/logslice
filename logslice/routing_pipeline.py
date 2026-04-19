"""High-level routing pipeline: parse -> filter -> route -> dispatch."""
from typing import Any, Callable, Dict, Iterable, List, Optional

from logslice.parser import parse_line
from logslice.router import Route, route_records
from logslice.dispatcher import dispatch

Record = Dict[str, Any]
Writer = Callable[[Iterable[Record]], None]


def routing_pipeline(
    lines: Iterable[str],
    routes: List[Route],
    writers: Dict[str, Writer],
    default_writer: Optional[Writer] = None,
    default_bucket: str = "default",
) -> Dict[str, int]:
    """Parse *lines*, route records, dispatch to writers.

    Returns per-bucket record counts.
    """
    records: List[Record] = []
    for line in lines:
        line = line.rstrip("\n")
        if not line:
            continue
        record = parse_line(line)
        if record is not None:
            records.append(record)

    buckets = route_records(records, routes, default=default_bucket)
    return dispatch(buckets, writers, default_writer=default_writer)

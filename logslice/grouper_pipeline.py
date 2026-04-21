"""High-level pipeline helpers that combine grouping with formatting."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional

from logslice.grouper import group_by_field, group_by_time_window


def grouped_summary(
    records: Iterable[dict],
    field: str,
    *,
    sort_keys: bool = True,
) -> List[dict]:
    """Return one summary record per unique value of *field*.

    Each summary contains:
      - the grouping field and its value
      - ``count`` – number of records in the group
    """
    groups = group_by_field(records, field)
    summaries = [
        {field: key, "count": len(members)}
        for key, members in groups.items()
    ]
    if sort_keys:
        summaries.sort(key=lambda r: r[field])
    return summaries


def time_window_summary(
    records: Iterable[dict],
    window_seconds: int,
    *,
    timestamp_field: str = "timestamp",
    extra_fields: Optional[List[str]] = None,
    aggregator: Optional[Callable[[List[dict]], dict]] = None,
) -> List[dict]:
    """Return one summary record per time window.

    Each summary contains:
      - ``window_start`` – ISO-8601 string for the window boundary
      - ``count`` – records in that window
      - any additional aggregated fields provided by *aggregator*

    *aggregator* receives the list of records for a window and should return
    a dict of extra key/value pairs to merge into the summary.
    """
    groups = group_by_time_window(
        records,
        window_seconds=window_seconds,
        timestamp_field=timestamp_field,
    )
    summaries: List[dict] = []
    for window_start, members in sorted(groups.items()):
        entry: dict = {"window_start": window_start, "count": len(members)}
        if aggregator is not None:
            entry.update(aggregator(members))
        summaries.append(entry)
    return summaries


def apply_per_group(
    records: Iterable[dict],
    field: str,
    fn: Callable[[str, List[dict]], List[dict]],
) -> Dict[str, List[dict]]:
    """Apply *fn(key, group_records)* to each group and return the results.

    Useful for running transforms or filters independently on each bucket.
    """
    groups = group_by_field(records, field)
    return {key: fn(key, members) for key, members in groups.items()}

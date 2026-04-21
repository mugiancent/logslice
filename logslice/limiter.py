"""Limit the number of records processed or emitted."""

from typing import Iterable, Iterator


def take(records: Iterable[dict], n: int) -> list[dict]:
    """Return at most *n* records from *records*.

    Args:
        records: Iterable of log record dicts.
        n: Maximum number of records to return.  Must be >= 0.

    Returns:
        A list containing the first ``n`` records (or fewer if the source
        is exhausted).

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    result: list[dict] = []
    for record in records:
        if len(result) >= n:
            break
        result.append(record)
    return result


def skip(records: Iterable[dict], n: int) -> list[dict]:
    """Skip the first *n* records and return the rest.

    Args:
        records: Iterable of log record dicts.
        n: Number of leading records to discard.  Must be >= 0.

    Returns:
        A list of records after the first *n* have been dropped.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    result: list[dict] = []
    skipped = 0
    for record in records:
        if skipped < n:
            skipped += 1
            continue
        result.append(record)
    return result


def take_last(records: Iterable[dict], n: int) -> list[dict]:
    """Return the last *n* records from *records*.

    Args:
        records: Iterable of log record dicts.
        n: Maximum number of trailing records to return.  Must be >= 0.

    Returns:
        A list containing the last ``n`` records.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if n == 0:
        return []
    buf: list[dict] = []
    for record in records:
        buf.append(record)
        if len(buf) > n:
            buf.pop(0)
    return buf


def slice_records(records: Iterable[dict], start: int, stop: int) -> list[dict]:
    """Return records at indices *[start, stop)*.

    Equivalent to ``list(records)[start:stop]`` but avoids materialising
    the full sequence before slicing.

    Args:
        records: Iterable of log record dicts.
        start: Inclusive start index (0-based).  Must be >= 0.
        stop: Exclusive stop index.  Must be >= *start*.

    Raises:
        ValueError: If *start* or *stop* are invalid.
    """
    if start < 0:
        raise ValueError(f"start must be >= 0, got {start}")
    if stop < start:
        raise ValueError(f"stop must be >= start, got stop={stop} start={start}")
    return skip(take(records, stop), start)

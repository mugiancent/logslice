"""Split records into multiple streams based on a field value or predicate."""
from typing import Callable, Dict, Iterable, List, Tuple


def split_by_field(
    records: Iterable[dict], field: str
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records that are missing the field are placed under the empty-string key.
    """
    buckets: Dict[str, List[dict]] = {}
    for record in records:
        key = str(record.get(field, ""))
        buckets.setdefault(key, []).append(record)
    return buckets


def split_by_predicate(
    records: Iterable[dict], predicate: Callable[[dict], bool]
) -> Tuple[List[dict], List[dict]]:
    """Split records into (matching, non-matching) based on *predicate*."""
    matched: List[dict] = []
    unmatched: List[dict] = []
    for record in records:
        (matched if predicate(record) else unmatched).append(record)
    return matched, unmatched


def split_by_value(
    records: Iterable[dict], field: str, values: Iterable[str]
) -> Tuple[List[dict], List[dict]]:
    """Split records into those whose *field* is in *values* and the rest."""
    value_set = set(values)
    return split_by_predicate(
        records, lambda r: str(r.get(field, "")) in value_set
    )


def split_chunks(
    records: Iterable[dict], size: int
) -> List[List[dict]]:
    """Divide *records* into sequential chunks of at most *size* each."""
    if size < 1:
        raise ValueError("size must be >= 1")
    chunks: List[List[dict]] = []
    chunk: List[dict] = []
    for record in records:
        chunk.append(record)
        if len(chunk) == size:
            chunks.append(chunk)
            chunk = []
    if chunk:
        chunks.append(chunk)
    return chunks

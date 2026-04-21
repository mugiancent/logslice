"""Join two sequences of records on a shared field value."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]


def _build_index(records: Iterable[Record], key: str) -> Dict[str, List[Record]]:
    """Index records by the value of *key*."""
    index: Dict[str, List[Record]] = {}
    for record in records:
        value = str(record.get(key, ""))
        index.setdefault(value, []).append(record)
    return index


def inner_join(
    left: Iterable[Record],
    right: Iterable[Record],
    on: str,
    right_prefix: str = "right_",
) -> Iterator[Record]:
    """Yield merged records where *on* matches in both sides."""
    index = _build_index(right, on)
    for left_rec in left:
        key_val = str(left_rec.get(on, ""))
        for right_rec in index.get(key_val, []):
            merged: Record = dict(left_rec)
            for k, v in right_rec.items():
                if k == on:
                    continue
                merged[right_prefix + k] = v
            yield merged


def left_join(
    left: Iterable[Record],
    right: Iterable[Record],
    on: str,
    right_prefix: str = "right_",
) -> Iterator[Record]:
    """Yield all left records; enrich with right data where *on* matches."""
    index = _build_index(right, on)
    for left_rec in left:
        key_val = str(left_rec.get(on, ""))
        matches = index.get(key_val, [])
        if matches:
            for right_rec in matches:
                merged: Record = dict(left_rec)
                for k, v in right_rec.items():
                    if k == on:
                        continue
                    merged[right_prefix + k] = v
                yield merged
        else:
            yield dict(left_rec)


def cross_join(
    left: Iterable[Record],
    right: Iterable[Record],
    right_prefix: str = "right_",
) -> Iterator[Record]:
    """Yield the Cartesian product of left and right records."""
    right_list = list(right)
    forfor right_rec in right_list:
            merged: Record = dict(left_rec)
            for k, v in right_rec.items():
                merged[right_prefix + k] = v
            yield merged

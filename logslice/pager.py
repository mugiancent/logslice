"""Paginated output helpers for logslice."""

from __future__ import annotations

from typing import Iterable, Iterator, List, TypeVar

T = TypeVar("T")


def paginate(items: List[T], page_size: int, page: int) -> List[T]:
    """Return a single page of *items*.

    Pages are 1-indexed.  If *page* is beyond the available pages the
    returned list will be empty.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if page < 1:
        raise ValueError(f"page must be >= 1, got {page}")
    start = (page - 1) * page_size
    return items[start : start + page_size]


def page_count(total: int, page_size: int) -> int:
    """Return the number of pages needed to display *total* items."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if total == 0:
        return 0
    return (total + page_size - 1) // page_size


def iter_pages(items: List[T], page_size: int) -> Iterator[List[T]]:
    """Yield successive pages of *items*."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    for start in range(0, len(items), page_size):
        yield items[start : start + page_size]

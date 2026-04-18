"""Tests for logslice.pager."""

import pytest
from logslice.pager import paginate, page_count, iter_pages

ITEMS = list(range(1, 11))  # [1 .. 10]


class TestPaginate:
    def test_first_page(self):
        assert paginate(ITEMS, page_size=3, page=1) == [1, 2, 3]

    def test_second_page(self):
        assert paginate(ITEMS, page_size=3, page=2) == [4, 5, 6]

    def test_last_partial_page(self):
        assert paginate(ITEMS, page_size=3, page=4) == [10]

    def test_page_beyond_end_returns_empty(self):
        assert paginate(ITEMS, page_size=3, page=99) == []

    def test_page_size_larger_than_items(self):
        assert paginate(ITEMS, page_size=100, page=1) == ITEMS

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            paginate(ITEMS, page_size=0, page=1)

    def test_invalid_page_raises(self):
        with pytest.raises(ValueError):
            paginate(ITEMS, page_size=3, page=0)


class TestPageCount:
    def test_exact_multiple(self):
        assert page_count(9, 3) == 3

    def test_partial_last_page(self):
        assert page_count(10, 3) == 4

    def test_zero_items(self):
        assert page_count(0, 5) == 0

    def test_single_item(self):
        assert page_count(1, 5) == 1

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            page_count(10, 0)


class TestIterPages:
    def test_yields_all_pages(self):
        pages = list(iter_pages(ITEMS, page_size=3))
        assert pages == [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

    def test_empty_input(self):
        assert list(iter_pages([], page_size=5)) == []

    def test_page_size_equals_length(self):
        assert list(iter_pages([1, 2], page_size=2)) == [[1, 2]]

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            list(iter_pages(ITEMS, page_size=0))

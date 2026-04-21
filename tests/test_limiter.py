"""Tests for logslice.limiter."""

import pytest

from logslice.limiter import take, skip, take_last, slice_records


RECORDS = [
    {"level": "info", "msg": "a"},
    {"level": "warn", "msg": "b"},
    {"level": "error", "msg": "c"},
    {"level": "debug", "msg": "d"},
    {"level": "info", "msg": "e"},
]


class TestTake:
    def test_returns_first_n(self):
        assert take(RECORDS, 3) == RECORDS[:3]

    def test_n_zero_returns_empty(self):
        assert take(RECORDS, 0) == []

    def test_n_larger_than_records_returns_all(self):
        assert take(RECORDS, 100) == RECORDS

    def test_exact_n_returns_all(self):
        assert take(RECORDS, len(RECORDS)) == RECORDS

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            take(RECORDS, -1)

    def test_does_not_mutate_source(self):
        original = list(RECORDS)
        take(RECORDS, 2)
        assert list(RECORDS) == original


class TestSkip:
    def test_skips_first_n(self):
        assert skip(RECORDS, 2) == RECORDS[2:]

    def test_n_zero_returns_all(self):
        assert skip(RECORDS, 0) == RECORDS

    def test_n_larger_than_records_returns_empty(self):
        assert skip(RECORDS, 100) == []

    def test_exact_n_returns_empty(self):
        assert skip(RECORDS, len(RECORDS)) == []

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            skip(RECORDS, -1)


class TestTakeLast:
    def test_returns_last_n(self):
        assert take_last(RECORDS, 2) == RECORDS[-2:]

    def test_n_zero_returns_empty(self):
        assert take_last(RECORDS, 0) == []

    def test_n_larger_than_records_returns_all(self):
        assert take_last(RECORDS, 100) == RECORDS

    def test_n_one_returns_last(self):
        assert take_last(RECORDS, 1) == [RECORDS[-1]]

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            take_last(RECORDS, -1)

    def test_empty_input(self):
        assert take_last([], 3) == []


class TestSliceRecords:
    def test_middle_slice(self):
        assert slice_records(RECORDS, 1, 4) == RECORDS[1:4]

    def test_from_start(self):
        assert slice_records(RECORDS, 0, 3) == RECORDS[:3]

    def test_empty_range(self):
        assert slice_records(RECORDS, 2, 2) == []

    def test_full_range(self):
        assert slice_records(RECORDS, 0, len(RECORDS)) == RECORDS

    def test_negative_start_raises(self):
        with pytest.raises(ValueError, match="start"):
            slice_records(RECORDS, -1, 3)

    def test_stop_less_than_start_raises(self):
        with pytest.raises(ValueError, match="stop"):
            slice_records(RECORDS, 3, 1)

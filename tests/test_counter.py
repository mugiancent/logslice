"""Tests for logslice.counter."""
import pytest
from logslice.counter import count_records, count_field_values, count_fields_present, top_n


RECORDS = [
    {"level": "info", "service": "web"},
    {"level": "error", "service": "web"},
    {"level": "info", "service": "db"},
    {"level": "info"},
]


class TestCountRecords:
    def test_empty(self):
        assert count_records([]) == 0

    def test_non_empty(self):
        assert count_records(RECORDS) == 4


class TestCountFieldValues:
    def test_counts_correctly(self):
        result = count_field_values(RECORDS, "level")
        assert result == {"info": 3, "error": 1}

    def test_missing_field_ignored(self):
        result = count_field_values(RECORDS, "service")
        assert result == {"web": 2, "db": 1}

    def test_nonexistent_field_returns_empty(self):
        result = count_field_values(RECORDS, "missing")
        assert result == {}

    def test_empty_records(self):
        assert count_field_values([], "level") == {}


class TestCountFieldsPresent:
    def test_all_present(self):
        result = count_fields_present(RECORDS, ["level"])
        assert result == {"level": 4}

    def test_partial_presence(self):
        result = count_fields_present(RECORDS, ["service"])
        assert result == {"service": 3}

    def test_multiple_fields(self):
        result = count_fields_present(RECORDS, ["level", "service"])
        assert result["level"] == 4
        assert result["service"] == 3

    def test_empty_fields_list(self):
        assert count_fields_present(RECORDS, []) == {}


class TestTopN:
    def test_returns_sorted(self):
        counts = {"a": 1, "b": 5, "c": 3}
        assert top_n(counts, 2) == [("b", 5), ("c", 3)]

    def test_n_larger_than_dict(self):
        counts = {"x": 2}
        assert top_n(counts, 10) == [("x", 2)]

    def test_invalid_n_raises(self):
        with pytest.raises(ValueError):
            top_n({}, 0)

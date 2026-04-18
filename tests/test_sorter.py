"""Tests for logslice.sorter."""

import pytest
from logslice.sorter import sort_records, deduplicate


RECORDS = [
    {"ts": "2024-01-03T10:00:00Z", "level": "info", "msg": "third"},
    {"ts": "2024-01-01T08:00:00Z", "level": "warn", "msg": "first"},
    {"ts": "2024-01-02T09:00:00Z", "level": "info", "msg": "second"},
]


class TestSortRecords:
    def test_sort_by_timestamp_ascending(self):
        result = sort_records(RECORDS)
        assert [r["msg"] for r in result] == ["first", "second", "third"]

    def test_sort_by_timestamp_descending(self):
        result = sort_records(RECORDS, reverse=True)
        assert [r["msg"] for r in result] == ["third", "second", "first"]

    def test_sort_by_custom_field(self):
        result = sort_records(RECORDS, key="level")
        levels = [r["level"] for r in result]
        assert levels == sorted(levels)

    def test_missing_key_goes_last(self):
        records = [
            {"val": 2},
            {"val": 1},
            {"other": "x"},  # missing 'val'
        ]
        result = sort_records(records, key="val")
        assert result[-1] == {"other": "x"}
        assert result[0]["val"] == 1

    def test_empty_input(self):
        assert sort_records([]) == []

    def test_no_timestamp_field_goes_last(self):
        records = [
            {"ts": "2024-01-02T00:00:00Z", "msg": "b"},
            {"msg": "no-ts"},
            {"ts": "2024-01-01T00:00:00Z", "msg": "a"},
        ]
        result = sort_records(records)
        assert result[-1]["msg"] == "no-ts"


class TestDeduplicate:
    def test_no_duplicates_unchanged(self):
        records = [{"a": 1}, {"a": 2}]
        assert deduplicate(records) == records

    def test_removes_full_duplicates(self):
        records = [{"a": 1}, {"a": 1}, {"a": 2}]
        result = deduplicate(records)
        assert len(result) == 2

    def test_dedup_by_key(self):
        records = [
            {"id": "x", "val": 1},
            {"id": "x", "val": 2},
            {"id": "y", "val": 3},
        ]
        result = deduplicate(records, key="id")
        assert len(result) == 2
        assert result[0] == {"id": "x", "val": 1}

    def test_missing_key_treated_as_none(self):
        records = [{"id": "a"}, {"other": 1}, {"other": 2}]
        result = deduplicate(records, key="id")
        # both missing-id records share None marker, only first kept
        assert len(result) == 2

    def test_empty_input(self):
        assert deduplicate([]) == []

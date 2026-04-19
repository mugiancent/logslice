"""Tests for logslice.deduplicator."""
import pytest
from logslice.deduplicator import deduplicate, count_duplicates


RECORDS = [
    {"level": "info", "msg": "started"},
    {"level": "info", "msg": "started"},
    {"level": "error", "msg": "failed"},
    {"level": "info", "msg": "started"},
]


class TestDeduplicate:
    def test_keep_first_removes_duplicates(self):
        result = list(deduplicate(RECORDS))
        assert result == [{"level": "info", "msg": "started"}, {"level": "error", "msg": "failed"}]

    def test_keep_last_returns_last_occurrence(self):
        records = [
            {"id": "1", "v": "a"},
            {"id": "1", "v": "b"},
            {"id": "2", "v": "c"},
        ]
        result = list(deduplicate(records, fields=["id"], keep="last"))
        assert result == [{"id": "1", "v": "b"}, {"id": "2", "v": "c"}]

    def test_fields_subset_deduplication(self):
        records = [
            {"level": "info", "ts": "1"},
            {"level": "info", "ts": "2"},
            {"level": "error", "ts": "3"},
        ]
        result = list(deduplicate(records, fields=["level"]))
        assert len(result) == 2
        assert result[0]["ts"] == "1"

    def test_empty_input(self):
        assert list(deduplicate([])) == []

    def test_no_duplicates_unchanged(self):
        records = [{"a": 1}, {"a": 2}, {"a": 3}]
        assert list(deduplicate(records)) == records

    def test_invalid_keep_raises(self):
        with pytest.raises(ValueError):
            list(deduplicate(RECORDS, keep="middle"))

    def test_all_duplicates_returns_one(self):
        records = [{"x": 1}] * 5
        assert list(deduplicate(records)) == [{"x": 1}]


class TestCountDuplicates:
    def test_counts_correctly(self):
        result = count_duplicates(RECORDS)
        counts = {r["msg"]: c for r, c in result}
        assert counts["started"] == 3
        assert counts["failed"] == 1

    def test_empty_returns_empty(self):
        assert count_duplicates([]) == []

    def test_field_subset_counting(self):
        records = [
            {"level": "info", "ts": "1"},
            {"level": "info", "ts": "2"},
        ]
        result = count_duplicates(records, fields=["level"])
        assert len(result) == 1
        assert result[0][1] == 2

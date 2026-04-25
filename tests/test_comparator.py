"""Tests for logslice.comparator."""

import pytest
from logslice.comparator import align_records, compare_records, summary


A = {"id": "1", "level": "info", "msg": "hello"}
B = {"id": "2", "level": "warn", "msg": "world"}
A2 = {"id": "1", "level": "error", "msg": "hello"}  # changed level
C = {"id": "3", "level": "debug", "msg": "new"}


class TestAlignRecords:
    def test_matching_keys_paired(self):
        pairs = list(align_records([A], [A2], key="id"))
        assert len(pairs) == 1
        assert pairs[0] == (A, A2)

    def test_left_only_has_none_right(self):
        pairs = list(align_records([A], [], key="id"))
        assert pairs == [(A, None)]

    def test_right_only_has_none_left(self):
        pairs = list(align_records([], [C], key="id"))
        assert pairs == [(None, C)]

    def test_multiple_records_all_aligned(self):
        pairs = list(align_records([A, B], [A2, B], key="id"))
        assert len(pairs) == 2


class TestCompareRecords:
    def test_equal_records(self):
        result = compare_records([A], [A], key="id")
        assert result[0]["status"] == "equal"
        assert result[0]["changes"] == []

    def test_changed_record(self):
        result = compare_records([A], [A2], key="id")
        assert result[0]["status"] == "changed"
        changes = result[0]["changes"]
        assert len(changes) == 1
        assert changes[0]["field"] == "level"
        assert changes[0]["left"] == "info"
        assert changes[0]["right"] == "error"

    def test_added_record(self):
        result = compare_records([], [C], key="id")
        assert result[0]["status"] == "added"
        assert result[0]["key_value"] == "3"

    def test_removed_record(self):
        result = compare_records([A], [], key="id")
        assert result[0]["status"] == "removed"
        assert result[0]["key_value"] == "1"

    def test_mixed_statuses(self):
        result = compare_records([A, B], [A2, C], key="id")
        statuses = {r["key_value"]: r["status"] for r in result}
        assert statuses["1"] == "changed"
        assert statuses["2"] == "removed"
        assert statuses["3"] == "added"

    def test_empty_both(self):
        assert compare_records([], [], key="id") == []


class TestSummary:
    def test_counts_all_statuses(self):
        comparisons = [
            {"status": "equal", "changes": []},
            {"status": "changed", "changes": []},
            {"status": "added", "changes": []},
            {"status": "removed", "changes": []},
        ]
        result = summary(comparisons)
        assert result == {"added": 1, "removed": 1, "changed": 1, "equal": 1}

    def test_empty_comparisons(self):
        result = summary([])
        assert result == {"added": 0, "removed": 0, "changed": 0, "equal": 0}

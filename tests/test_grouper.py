"""Tests for logslice.grouper."""

from __future__ import annotations

import pytest

from logslice.grouper import group_by_field, group_by_time_window, merge_groups


# ---------------------------------------------------------------------------
# group_by_field
# ---------------------------------------------------------------------------

class TestGroupByField:
    def test_groups_correctly(self):
        records = [
            {"level": "info", "msg": "a"},
            {"level": "error", "msg": "b"},
            {"level": "info", "msg": "c"},
        ]
        result = group_by_field(records, "level")
        assert set(result.keys()) == {"info", "error"}
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1

    def test_missing_field_goes_to_empty_key(self):
        records = [{"msg": "no level"}]
        result = group_by_field(records, "level")
        assert "" in result
        assert result[""][0]["msg"] == "no level"

    def test_empty_records(self):
        assert group_by_field([], "level") == {}

    def test_all_same_value(self):
        records = [{"level": "debug"} for _ in range(5)]
        result = group_by_field(records, "level")
        assert list(result.keys()) == ["debug"]
        assert len(result["debug"]) == 5


# ---------------------------------------------------------------------------
# group_by_time_window
# ---------------------------------------------------------------------------

class TestGroupByTimeWindow:
    def test_same_window(self):
        records = [
            {"timestamp": "2024-01-01T00:00:05Z"},
            {"timestamp": "2024-01-01T00:00:45Z"},
        ]
        result = group_by_time_window(records, window_seconds=60)
        assert len(result) == 1
        assert len(list(result.values())[0]) == 2

    def test_different_windows(self):
        records = [
            {"timestamp": "2024-01-01T00:00:05Z"},
            {"timestamp": "2024-01-01T00:01:05Z"},
        ]
        result = group_by_time_window(records, window_seconds=60)
        assert len(result) == 2

    def test_missing_timestamp_goes_to_empty_key(self):
        records = [{"msg": "no ts"}]
        result = group_by_time_window(records, window_seconds=60)
        assert "" in result

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            group_by_time_window([], window_seconds=0)

    def test_negative_window_raises(self):
        with pytest.raises(ValueError):
            group_by_time_window([], window_seconds=-10)

    def test_empty_records(self):
        assert group_by_time_window([], window_seconds=60) == {}


# ---------------------------------------------------------------------------
# merge_groups
# ---------------------------------------------------------------------------

class TestMergeGroups:
    def test_merges_disjoint_keys(self):
        a = {"info": [{"msg": "x"}]}
        b = {"error": [{"msg": "y"}]}
        result = merge_groups(a, b)
        assert set(result.keys()) == {"info", "error"}

    def test_merges_overlapping_keys(self):
        a = {"info": [{"msg": "x"}]}
        b = {"info": [{"msg": "y"}]}
        result = merge_groups(a, b)
        assert len(result["info"]) == 2

    def test_empty_inputs(self):
        assert merge_groups({}, {}) == {}

    def test_single_input(self):
        a = {"debug": [{"msg": "z"}]}
        assert merge_groups(a) == a

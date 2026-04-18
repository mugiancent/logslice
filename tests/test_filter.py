"""Tests for logslice.filter module."""

from datetime import datetime

import pytest

from logslice.filter import filter_by_field, filter_by_time


ENTRIES = [
    {"timestamp": "2024-01-01T10:00:00", "level": "info", "msg": "start"},
    {"timestamp": "2024-01-01T11:00:00", "level": "warn", "msg": "mid"},
    {"timestamp": "2024-01-01T12:00:00", "level": "error", "msg": "end"},
    {"level": "info", "msg": "no-timestamp"},
]


class TestFilterByTime:
    def test_no_bounds_returns_all(self):
        assert filter_by_time(ENTRIES) == ENTRIES

    def test_start_only(self):
        start = datetime(2024, 1, 1, 10, 30)
        result = filter_by_time(ENTRIES, start=start)
        assert len(result) == 2
        assert result[0]["msg"] == "mid"
        assert result[1]["msg"] == "end"

    def test_end_only(self):
        end = datetime(2024, 1, 1, 11, 0)
        result = filter_by_time(ENTRIES, end=end)
        assert len(result) == 2
        assert result[0]["msg"] == "start"

    def test_start_and_end(self):
        start = datetime(2024, 1, 1, 10, 30)
        end = datetime(2024, 1, 1, 11, 30)
        result = filter_by_time(ENTRIES, start=start, end=end)
        assert len(result) == 1
        assert result[0]["msg"] == "mid"

    def test_entries_without_timestamp_excluded(self):
        start = datetime(2024, 1, 1, 9, 0)
        result = filter_by_time(ENTRIES, start=start)
        msgs = [e["msg"] for e in result]
        assert "no-timestamp" not in msgs

    def test_unix_timestamp(self):
        entries = [{"ts": 1704067200.0, "msg": "unix"}]  # 2024-01-01T00:00:00
        result = filter_by_time(entries, start=datetime(2023, 12, 31))
        assert len(result) == 1


class TestFilterByField:
    def test_match_level(self):
        result = filter_by_field(ENTRIES, "level", "info")
        assert len(result) == 2

    def test_no_match(self):
        result = filter_by_field(ENTRIES, "level", "debug")
        assert result == []

    def test_missing_field_excluded(self):
        entries = [{"msg": "a"}, {"msg": "b", "level": "info"}]
        result = filter_by_field(entries, "level", "info")
        assert len(result) == 1

"""Tests for logslice.timeshift."""

from datetime import datetime, timedelta, timezone

import pytest

from logslice.timeshift import (
    _parse_ts,
    normalise_to_utc,
    rebase_records,
    shift_record,
    shift_records,
)

UTC = timezone.utc


class TestParseTs:
    def test_parses_utc_z_suffix(self):
        dt = _parse_ts("2024-01-15T10:00:00Z")
        assert dt == datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)

    def test_parses_offset(self):
        dt = _parse_ts("2024-01-15T12:00:00+02:00")
        assert dt.utcoffset() == timedelta(hours=2)

    def test_parses_fractional_seconds(self):
        dt = _parse_ts("2024-01-15T10:00:00.123456Z")
        assert dt.microsecond == 123456

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            _parse_ts("not-a-timestamp")


class TestShiftRecord:
    def test_shifts_forward(self):
        rec = {"timestamp": "2024-01-15T10:00:00Z", "msg": "hello"}
        result = shift_record(rec, timedelta(hours=1))
        assert "2024-01-15T11:00:00" in result["timestamp"]

    def test_shifts_backward(self):
        rec = {"timestamp": "2024-01-15T10:00:00Z"}
        result = shift_record(rec, timedelta(hours=-2))
        assert "2024-01-15T08:00:00" in result["timestamp"]

    def test_missing_field_returns_unchanged(self):
        rec = {"msg": "no ts"}
        result = shift_record(rec, timedelta(hours=1))
        assert result == rec

    def test_unparseable_field_returns_unchanged(self):
        rec = {"timestamp": "bad-value"}
        result = shift_record(rec, timedelta(hours=1))
        assert result["timestamp"] == "bad-value"

    def test_does_not_mutate_original(self):
        rec = {"timestamp": "2024-01-15T10:00:00Z"}
        _ = shift_record(rec, timedelta(minutes=30))
        assert rec["timestamp"] == "2024-01-15T10:00:00Z"

    def test_custom_field(self):
        rec = {"ts": "2024-01-15T10:00:00Z"}
        result = shift_record(rec, timedelta(minutes=5), field="ts")
        assert "2024-01-15T10:05:00" in result["ts"]


class TestShiftRecords:
    def test_shifts_all(self):
        records = [
            {"timestamp": "2024-01-15T10:00:00Z"},
            {"timestamp": "2024-01-15T11:00:00Z"},
        ]
        results = list(shift_records(records, timedelta(hours=1)))
        assert "2024-01-15T11:00:00" in results[0]["timestamp"]
        assert "2024-01-15T12:00:00" in results[1]["timestamp"]


class TestNormaliseToUtc:
    def test_converts_offset_to_utc(self):
        rec = {"timestamp": "2024-01-15T12:00:00+02:00"}
        result = normalise_to_utc(rec)
        assert "+00:00" in result["timestamp"] or result["timestamp"].endswith("Z")
        assert "10:00:00" in result["timestamp"]

    def test_missing_field_unchanged(self):
        rec = {"msg": "hi"}
        assert normalise_to_utc(rec) == rec


class TestRebaseRecords:
    def test_earliest_aligns_to_new_start(self):
        records = [
            {"timestamp": "2024-01-15T10:00:00Z"},
            {"timestamp": "2024-01-15T10:05:00Z"},
        ]
        new_start = datetime(2024, 6, 1, 0, 0, 0, tzinfo=UTC)
        results = list(rebase_records(records, new_start))
        first_dt = _parse_ts(results[0]["timestamp"])
        assert first_dt == new_start

    def test_relative_gap_preserved(self):
        records = [
            {"timestamp": "2024-01-15T10:00:00Z"},
            {"timestamp": "2024-01-15T10:10:00Z"},
        ]
        new_start = datetime(2024, 6, 1, 0, 0, 0, tzinfo=UTC)
        results = list(rebase_records(records, new_start))
        t0 = _parse_ts(results[0]["timestamp"])
        t1 = _parse_ts(results[1]["timestamp"])
        assert t1 - t0 == timedelta(minutes=10)

    def test_no_timestamp_field_yields_unchanged(self):
        records = [{"msg": "a"}, {"msg": "b"}]
        new_start = datetime(2024, 6, 1, tzinfo=UTC)
        results = list(rebase_records(records, new_start))
        assert results == records

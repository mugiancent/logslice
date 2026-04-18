"""Tests for logslice.aggregator."""
import pytest
from logslice.aggregator import count_by, group_by, summarise

RECORDS = [
    {"level": "info", "duration_ms": "120"},
    {"level": "info", "duration_ms": "80"},
    {"level": "error", "duration_ms": "300"},
    {"level": "warn"},
    {"duration_ms": "50"},
]


class TestGroupBy:
    def test_groups_by_existing_field(self):
        groups = group_by(RECORDS, "level")
        assert set(groups.keys()) == {"info", "error", "warn", ""}
        assert len(groups["info"]) == 2

    def test_missing_field_goes_to_empty_key(self):
        groups = group_by(RECORDS, "level")
        assert len(groups[""]) == 1

    def test_empty_records(self):
        assert group_by([], "level") == {}

    def test_all_missing_field(self):
        records = [{"a": 1}, {"b": 2}]
        groups = group_by(records, "level")
        assert list(groups.keys()) == [""]
        assert len(groups[""]) == 2


class TestCountBy:
    def test_counts_correctly(self):
        counts = count_by(RECORDS, "level")
        assert counts["info"] == 2
        assert counts["error"] == 1
        assert counts["warn"] == 1
        assert counts[""] == 1

    def test_empty_records(self):
        assert count_by([], "level") == {}


class TestSummarise:
    def test_count_only(self):
        result = summarise(RECORDS, "level")
        by_key = {r["level"]: r for r in result}
        assert by_key["info"]["count"] == 2
        assert "sum" not in by_key["info"]

    def test_numeric_aggregation(self):
        result = summarise(RECORDS, "level", numeric_field="duration_ms")
        by_key = {r["level"]: r for r in result}
        assert by_key["info"]["sum"] == pytest.approx(200.0)
        assert by_key["info"]["min"] == pytest.approx(80.0)
        assert by_key["info"]["max"] == pytest.approx(120.0)

    def test_missing_numeric_values_skipped(self):
        result = summarise(RECORDS, "level", numeric_field="duration_ms")
        by_key = {r["level"]: r for r in result}
        # 'warn' record has no duration_ms
        assert "sum" not in by_key["warn"]

    def test_sorted_output(self):
        result = summarise(RECORDS, "level")
        keys = [r["level"] for r in result]
        assert keys == sorted(keys)

    def test_empty_records(self):
        assert summarise([], "level") == []

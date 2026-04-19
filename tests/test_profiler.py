"""Tests for logslice.profiler."""
import pytest
from logslice.profiler import profile_fields, field_names, coverage_report


RECORDS = [
    {"level": "info", "msg": "started", "pid": 1},
    {"level": "warn", "msg": "slow", "latency": 1.5},
    {"level": "error", "msg": "boom"},
]


class TestProfileFields:
    def test_counts_present_fields(self):
        p = profile_fields(RECORDS)
        assert p["level"]["count"] == 3
        assert p["msg"]["count"] == 3
        assert p["pid"]["count"] == 1
        assert p["latency"]["count"] == 1

    def test_coverage_full_field(self):
        p = profile_fields(RECORDS)
        assert p["level"]["coverage"] == pytest.approx(1.0)

    def test_coverage_partial_field(self):
        p = profile_fields(RECORDS)
        assert p["pid"]["coverage"] == pytest.approx(1 / 3)

    def test_type_inference_str(self):
        p = profile_fields(RECORDS)
        assert p["level"]["types"] == {"str": 3}

    def test_type_inference_float(self):
        p = profile_fields(RECORDS)
        assert p["latency"]["types"] == {"float": 1}

    def test_empty_records(self):
        assert profile_fields([]) == {}


class TestFieldNames:
    def test_returns_sorted_names(self):
        names = field_names(RECORDS)
        assert names == sorted({"level", "msg", "pid", "latency"})

    def test_empty_records(self):
        assert field_names([]) == []

    def test_deduplicates(self):
        recs = [{"a": 1}, {"a": 2, "b": 3}]
        assert field_names(recs) == ["a", "b"]


class TestCoverageReport:
    def test_sorted_by_coverage_desc(self):
        p = profile_fields(RECORDS)
        report = coverage_report(p)
        coverages = [r["coverage"] for r in report]
        assert coverages == sorted(coverages, reverse=True)

    def test_contains_all_fields(self):
        p = profile_fields(RECORDS)
        report = coverage_report(p)
        names = {r["field"] for r in report}
        assert names == {"level", "msg", "pid", "latency"}

    def test_empty_profile(self):
        assert coverage_report({}) == []

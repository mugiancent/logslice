"""Tests for logslice.bucketer."""

import pytest

from logslice.bucketer import (
    bucket_by_range,
    bucket_by_value,
    bucket_counts,
    top_buckets,
)


RECORDS = [
    {"level": "info", "latency": 10},
    {"level": "warn", "latency": 55},
    {"level": "info", "latency": 20},
    {"level": "error", "latency": 200},
    {"level": "warn", "latency": 80},
]


class TestBucketByValue:
    def test_groups_correctly(self):
        result = bucket_by_value(RECORDS, "level")
        assert set(result.keys()) == {"info", "warn", "error"}
        assert len(result["info"]) == 2
        assert len(result["warn"]) == 2
        assert len(result["error"]) == 1

    def test_missing_field_goes_to_empty_key(self):
        records = [{"x": 1}, {"level": "info"}]
        result = bucket_by_value(records, "level")
        assert "" in result
        assert len(result[""] ) == 1

    def test_empty_records(self):
        assert bucket_by_value([], "level") == {}

    def test_all_same_value(self):
        records = [{"level": "debug"} for _ in range(4)]
        result = bucket_by_value(records, "level")
        assert list(result.keys()) == ["debug"]
        assert len(result["debug"]) == 4


class TestBucketByRange:
    def test_basic_binning(self):
        result = bucket_by_range(RECORDS, "latency", [50, 100])
        assert len(result["[-inf,50.0)"] ) == 2   # 10, 20
        assert len(result["[50.0,100.0)"] ) == 2  # 55, 80
        assert len(result["[100.0,+inf)"] ) == 1  # 200

    def test_custom_labels(self):
        result = bucket_by_range(
            RECORDS, "latency", [50, 100], labels=["low", "mid", "high"]
        )
        assert "low" in result
        assert "mid" in result
        assert "high" in result
        assert len(result["low"]) == 2

    def test_wrong_label_count_raises(self):
        with pytest.raises(ValueError, match="labels length"):
            bucket_by_range(RECORDS, "latency", [50], labels=["a", "b", "c"])

    def test_non_numeric_field_skipped(self):
        records = [{"latency": "fast"}, {"latency": 10}]
        result = bucket_by_range(records, "latency", [50])
        total = sum(len(v) for v in result.values())
        assert total == 1

    def test_empty_input(self):
        result = bucket_by_range([], "latency", [50, 100])
        assert all(len(v) == 0 for v in result.values())


class TestBucketCounts:
    def test_counts_match_lengths(self):
        buckets = bucket_by_value(RECORDS, "level")
        counts = bucket_counts(buckets)
        assert counts == {"info": 2, "warn": 2, "error": 1}

    def test_empty_buckets(self):
        assert bucket_counts({}) == {}


class TestTopBuckets:
    def test_returns_sorted_descending(self):
        buckets = bucket_by_value(RECORDS, "level")
        top = top_buckets(buckets, n=2)
        assert len(top) == 2
        assert top[0][1] >= top[1][1]

    def test_n_larger_than_buckets(self):
        buckets = bucket_by_value(RECORDS, "level")
        top = top_buckets(buckets, n=100)
        assert len(top) == 3

    def test_empty(self):
        assert top_buckets({}) == []

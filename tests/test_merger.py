"""Tests for logslice.merger."""

import pytest
from logslice.merger import merge_sorted, merge_unsorted


def ts(val: str) -> dict:
    return {"timestamp": val, "msg": val}


class TestMergeSorted:
    def test_two_streams_interleaved(self):
        a = [ts("2024-01-01"), ts("2024-01-03")]
        b = [ts("2024-01-02"), ts("2024-01-04")]
        result = list(merge_sorted(a, b))
        assert [r["timestamp"] for r in result] == [
            "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"
        ]

    def test_empty_stream_ignored(self):
        a = [ts("2024-01-01"), ts("2024-01-02")]
        b: list[dict] = []
        result = list(merge_sorted(a, b))
        assert len(result) == 2

    def test_all_empty_streams(self):
        result = list(merge_sorted([], [], []))
        assert result == []

    def test_single_stream_passthrough(self):
        a = [ts("2024-01-01"), ts("2024-01-02"), ts("2024-01-03")]
        result = list(merge_sorted(a))
        assert result == a

    def test_custom_key(self):
        a = [{"level": "a", "v": 1}, {"level": "c", "v": 3}]
        b = [{"level": "b", "v": 2}]
        result = list(merge_sorted(a, b, key="level"))
        assert [r["v"] for r in result] == [1, 2, 3]

    def test_missing_timestamp_sorts_first(self):
        a = [{"msg": "no-ts"}, ts("2024-01-01")]
        b = [ts("2024-01-02")]
        result = list(merge_sorted(a, b))
        assert result[0]["msg"] == "no-ts"

    def test_three_streams(self):
        a = [ts("2024-01-01"), ts("2024-01-04")]
        b = [ts("2024-01-02"), ts("2024-01-05")]
        c = [ts("2024-01-03"), ts("2024-01-06")]
        result = list(merge_sorted(a, b, c))
        timestamps = [r["timestamp"] for r in result]
        assert timestamps == sorted(timestamps)


class TestMergeUnsorted:
    def test_sorts_across_streams(self):
        a = [ts("2024-01-03"), ts("2024-01-01")]
        b = [ts("2024-01-02")]
        result = merge_unsorted(a, b)
        assert [r["timestamp"] for r in result] == [
            "2024-01-01", "2024-01-02", "2024-01-03"
        ]

    def test_empty_inputs(self):
        assert merge_unsorted([], []) == []

    def test_custom_key_unsorted(self):
        a = [{"score": "30"}, {"score": "10"}]
        b = [{"score": "20"}]
        result = merge_unsorted(a, b, key="score")
        assert [r["score"] for r in result] == ["10", "20", "30"]
